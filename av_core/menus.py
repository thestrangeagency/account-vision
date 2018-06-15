NAV_MENU_LEFT = [
    {
        "name": "Features",
        "url": "features",
        "validators": ["menu_generator.validators.is_anonymous"],
    },
    {
        "name": "Pricing",
        "url": "pricing",
        "validators": ["menu_generator.validators.is_anonymous"],
    },
    {
        "name": "Tax Years",
        "url": "returns",
        "validators": ["menu_generator.validators.is_authenticated", "av_core.menus.is_not_cpa"],
        "root": True,
    },
    {
        "name": "Clients",
        "url": "clients",
        "validators": ["menu_generator.validators.is_authenticated", "av_core.menus.is_cpa"],
        "root": True,
    },
    {
        "name": "Messages",
        "url": "messages_redirect",
        "validators": ["menu_generator.validators.is_authenticated"],
        "root": True,
    },
    {
        "name": "Team",
        "url": "team",
        "validators": ["menu_generator.validators.is_authenticated", "av_core.menus.is_admin"],
        "root": True,
    },
    {
        "name": "Profile",
        "url": "identity",
        "validators": ["menu_generator.validators.is_authenticated", "av_core.menus.is_not_cpa"],
        "root": True,
    },
    {
        "name": "Account",
        "url": "edit",
        "validators": ["menu_generator.validators.is_authenticated"],
    },
    # {
    #     "name": "Uploads",
    #     "url": reverse_lazy('cpa-user'),
    #     "validators": ["av_core.menus.is_cpa"],
    # },
]

NAV_MENU_RIGHT = [
    {
        "name": "Sign In",
        "url": "login",
        "validators": ["menu_generator.validators.is_anonymous"],
    },
    {
        "name": "Sign Out",
        "url": "logout",
        "validators": ["menu_generator.validators.is_authenticated"],
    },
]


def is_cpa(request):
    return not request.user.is_anonymous() and request.user.is_cpa


def is_admin(request):
    return not request.user.is_anonymous() and request.user.is_admin()


def is_not_cpa(request):
    return request.user.is_anonymous() or not request.user.is_cpa
