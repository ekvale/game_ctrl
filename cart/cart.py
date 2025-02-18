from decimal import Decimal
from django.conf import settings
from products.models import Controller

class Cart:
    def __init__(self, request):
        """Initialize the cart."""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, controller, quantity=1, override_quantity=False):
        """Add a controller to the cart or update its quantity."""
        controller_id = str(controller.id)
        if controller_id not in self.cart:
            self.cart[controller_id] = {'quantity': 0,
                                      'price': str(controller.price)}
        if override_quantity:
            self.cart[controller_id]['quantity'] = quantity
        else:
            self.cart[controller_id]['quantity'] += quantity
        self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def remove(self, controller):
        """Remove a controller from the cart."""
        controller_id = str(controller.id)
        if controller_id in self.cart:
            del self.cart[controller_id]
            self.save()

    def __iter__(self):
        """Iterate over the items in the cart and get the controllers from the database."""
        controller_ids = self.cart.keys()
        # get the controller objects and add them to the cart
        controllers = Controller.objects.filter(id__in=controller_ids)
        cart = self.cart.copy()
        for controller in controllers:
            cart[str(controller.id)]['controller'] = controller
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Count all items in the cart."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save() 