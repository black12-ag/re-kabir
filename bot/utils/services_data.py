# Sample services data for when the API is unavailable
SERVICES = [
    {
        "service": 1,
        "name": "Followers",
        "type": "Default",
        "category": "First Category",
        "rate": 0.99,
        "min": 50,
        "max": 10000,
        "refill": True
    },
    {
        "service": 2,
        "name": "Comments",
        "type": "Custom Comments",
        "category": "Second Category",
        "rate": 8,
        "min": 10,
        "max": 1500,
        "refill": False
    },
    {
        "service": 3,
        "name": "Likes",
        "type": "Default",
        "category": "First Category",
        "rate": 0.50,
        "min": 100,
        "max": 5000,
        "refill": True
    },
    {
        "service": 4,
        "name": "Views",
        "type": "Default",
        "category": "First Category",
        "rate": 0.10,
        "min": 1000,
        "max": 50000,
        "refill": False
    },
    {
        "service": 5,
        "name": "Shares",
        "type": "Default",
        "category": "Second Category",
        "rate": 1.50,
        "min": 50,
        "max": 2000,
        "refill": False
    }
]

# Group services by categories
CATEGORIES = {}
for service in SERVICES:
    category = service["category"]
    if category not in CATEGORIES:
        CATEGORIES[category] = []
    CATEGORIES[category].append(service)
