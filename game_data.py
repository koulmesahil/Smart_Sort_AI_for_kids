"""
Game data definitions for SmartSort Kids app.
This file contains the food categories and items used in the sorting game.
"""

# Standard food categories
FOOD_CATEGORIES = {
    "Fruits": ["🍎 Apple", "🍌 Banana", "🍊 Orange", "🍓 Strawberry", "🍇 Grapes", "🍉 Watermelon", 
              "🍐 Pear", "🥭 Mango", "🍍 Pineapple", "🍒 Cherries"],
    
    "Vegetables": ["🥕 Carrot", "🥦 Broccoli", "🍅 Tomato", "🥬 Lettuce", "🥒 Cucumber", "🌽 Corn",
                  "🥔 Potato", "🧅 Onion", "🍄 Mushroom", "🌶️ Pepper"],
    
    "Dairy": ["🧀 Cheese", "🥛 Milk", "🍦 Ice Cream", "🧈 Butter", "🥄 Yogurt",
             "🍨 Cream", "🧁 Custard"],
    
    "Grains": ["🍞 Bread", "🥣 Cereal", "🍝 Pasta", "🍚 Rice", "🥯 Bagel",
              "🥐 Croissant", "🥖 Baguette", "🌮 Tortilla"],
    
    "Protein": ["🥚 Egg", "🥜 Peanuts", "🍗 Chicken", "🐟 Fish", "🥩 Meat",
               "🦐 Shrimp", "🫘 Beans", "🍖 Meat on Bone"]
}

# Advanced categories for higher levels
ADVANCED_CATEGORIES = {
    "Healthy": ["🍎 Apple", "🥕 Carrot", "🥦 Broccoli", "🥒 Cucumber", "🥬 Lettuce", 
               "🥛 Milk", "🥚 Egg", "🍇 Grapes", "🍌 Banana", "🫘 Beans",
               "🥜 Peanuts", "🍚 Rice", "🐟 Fish", "🥔 Potato", "🍅 Tomato"],
    
    "Sometimes Foods": ["🍦 Ice Cream", "🍩 Donut", "🍪 Cookie", "🍫 Chocolate", "🍕 Pizza",
                      "🍟 French Fries", "🍔 Hamburger", "🥤 Soda", "🍬 Candy", "🍰 Cake"]
}

# Activity labels and descriptions for game levels
LEVEL_DESCRIPTIONS = {
    1: "Easy sorting with just fruits and vegetables.",
    2: "Added dairy items to the mix!",
    3: "Now with grains too - getting trickier!",
    4: "All food groups included - expert level!",
    5: "Advanced sorting based on healthy choices!"
}

# Educational fun facts about food groups
FOOD_FACTS = {
    "Fruits": [
        "Fruits are nature's sweet treats and full of vitamins!",
        "Most fruits grow on trees or bushes.",
        "Fruits have seeds inside them.",
        "Eating fruits helps keep your body healthy!"
    ],
    "Vegetables": [
        "Vegetables help you grow strong and healthy!",
        "Many vegetables grow underground, like carrots.",
        "Vegetables give your body important nutrients.",
        "Green vegetables have special nutrients called iron!"
    ],
    "Dairy": [
        "Dairy foods come from animal milk, usually cows.",
        "Dairy helps build strong bones and teeth!",
        "Cheese is made from milk that's been processed.",
        "Yogurt has good bacteria that helps your tummy!"
    ],
    "Grains": [
        "Grains give you energy to play all day!",
        "Bread, pasta, and cereal are all made from grains.",
        "Grains are the seeds of special grasses.",
        "Brown grains like brown rice have more nutrients than white ones."
    ],
    "Protein": [
        "Protein foods help build strong muscles!",
        "Protein can come from animals or plants.",
        "Beans and nuts are proteins that grow from plants.",
        "Your body needs protein to grow and heal."
    ]
}