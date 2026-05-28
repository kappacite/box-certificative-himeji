from app import create_app
from dao import db
from dao.models import UserModel, PlaceModel

# 200 Notable Places in France with accurate coordinates
NOTABLE_PLACES = [
    # Paris & Île-de-France (1-30)
    ("Tour Eiffel, Paris", 48.8584, 2.2945),
    ("Musée du Louvre, Paris", 48.8606, 2.3376),
    ("Cathédrale Notre-Dame, Paris", 48.8530, 2.3499),
    ("Arc de Triomphe, Paris", 48.8738, 2.2950),
    ("Sacré-Cœur de Montmartre, Paris", 48.8867, 2.3431),
    ("Château de Versailles", 48.8049, 2.1204),
    ("Panthéon, Paris", 48.8462, 2.3464),
    ("Sainte-Chapelle, Paris", 48.8554, 2.3450),
    ("Musée d'Orsay, Paris", 48.8599, 2.3265),
    ("Centre Pompidou, Paris", 48.8606, 2.3522),
    ("Jardin du Luxembourg, Paris", 48.8462, 2.3371),
    ("Palais Garnier, Paris", 48.8719, 2.3316),
    ("Champs-Élysées, Paris", 48.8698, 2.3075),
    ("Place de la Concorde, Paris", 48.8656, 2.3212),
    ("Pont Alexandre III, Paris", 48.8639, 2.3136),
    ("Musée de l'Orangerie, Paris", 48.8638, 2.3226),
    ("Les Invalides, Paris", 48.8566, 2.3127),
    ("Musée du Quai Branly, Paris", 48.8609, 2.2975),
    ("Fondation Louis Vuitton, Paris", 48.8766, 2.2634),
    ("Jardin des Tuileries, Paris", 48.8635, 2.3274),
    ("Place des Vosges, Paris", 48.8550, 2.3622),
    ("Catacombes de Paris", 48.8338, 2.3324),
    ("Cimetière du Père-Lachaise, Paris", 48.8614, 2.3933),
    ("Grande Arche de la Défense, Puteaux", 48.8928, 2.2361),
    ("Palais de Fontainebleau", 48.4021, 2.6997),
    ("Château de Vaux-le-Vicomte", 48.5658, 2.7141),
    ("Parc de Sceaux", 48.7739, 2.2974),
    ("Château de Vincennes", 48.8427, 2.4361),
    ("Basilique de Saint-Denis", 48.9355, 2.3598),
    ("Disneyland Paris, Marne-la-Vallée", 48.8722, 2.7758),
    # Normandy & Brittany (31-60)
    ("Mont Saint-Michel", 48.6361, -1.5115),
    ("Falaises d'Étretat", 49.7073, 0.2018),
    ("Cathédrale de Rouen", 49.4402, 1.0949),
    ("Gros-Horloge, Rouen", 49.4419, 1.0910),
    ("Tapisserie de Bayeux", 49.2744, -0.7011),
    ("Mémorial de Caen", 49.2008, -0.3789),
    ("Château de Caen", 49.1867, -0.3628),
    ("Vieux Bassin, Honfleur", 49.4194, 0.2333),
    ("Plages du Débarquement, Colleville-sur-Mer", 49.3592, -0.8436),
    ("Port militaire de Cherbourg", 49.6450, -1.6350),
    ("Phare de Gatteville", 49.6974, -1.2657),
    ("Fondation Claude Monet, Giverny", 49.0753, 1.5339),
    ("Alignements de Carnac", 47.5906, -3.0817),
    ("Cité Corsaire, Saint-Malo", 48.6490, -2.0260),
    ("Remparts de Vannes", 47.6582, -2.7561),
    ("Cathédrale de Rennes", 48.1114, -1.6853),
    ("Parlement de Bretagne, Rennes", 48.1128, -1.6778),
    ("Château des ducs de Bretagne, Nantes", 47.2162, -1.5499),
    ("Les Machines de l'Île, Nantes", 47.2057, -1.5642),
    ("Côte de Granit Rose, Ploumanac'h", 48.8319, -3.4800),
    ("Phare du Petit Minou, Plouzané", 48.3377, -4.6148),
    ("Pointe du Raz", 48.0392, -4.7378),
    ("Concarneau - Ville Close", 47.8727, -3.9189),
    ("Quimper - Cathédrale Saint-Corentin", 47.9961, -4.1025),
    ("Brest - Château de Brest", 48.3811, -4.4947),
    ("Golfe du Morbihan", 47.5960, -2.7930),
    ("Foret de Paimpont (Brocéliande)", 48.0167, -2.1667),
    ("Jardin du Thabor, Rennes", 48.1142, -1.6698),
    ("Océanopolis, Brest", 48.3897, -4.4375),
    ("Dinan - Château de Dinan", 48.4502, -2.0433),
    # Hauts-de-France & Grand Est (61-90)
    ("Grand-Place de Lille", 50.6369, 3.0636),
    ("Vieille Bourse, Lille", 50.6372, 3.0645),
    ("Beffroi de Lille", 50.6303, 3.0703),
    ("La Piscine, Roubaix", 50.6925, 3.1678),
    ("Château de Chantilly", 49.1939, 2.4853),
    ("Château de Pierrefonds", 49.3469, 2.9806),
    ("Cathédrale d'Amiens", 49.8949, 2.3023),
    ("Baie de Somme", 50.1878, 1.5833),
    ("Cathédrale Notre-Dame, Strasbourg", 48.5817, 7.7508),
    ("Petite France, Strasbourg", 48.5809, 7.7423),
    ("Parlement Européen, Strasbourg", 48.5975, 7.7717),
    ("Château du Haut-Koenigsbourg, Orschwiller", 48.2494, 7.3442),
    ("Petite Venise, Colmar", 48.0736, 7.3592),
    ("Musée Unterlinden, Colmar", 48.0797, 7.3556),
    ("Cathédrale de Reims", 49.2537, 4.0341),
    ("Palais du Tau, Reims", 49.2536, 4.0350),
    ("Place Stanislas, Nancy", 48.6936, 6.1832),
    ("Maison de Jeanne d'Arc, Domrémy-la-Pucelle", 48.4428, 5.6749),
    ("Centre Pompidou-Metz", 49.1083, 6.1817),
    ("Cathédrale Saint-Étienne, Metz", 49.1202, 6.1754),
    ("Ligne Maginot - Fort de Schoenenbourg", 48.9664, 7.8767),
    ("Citadelle de Belfort", 47.6369, 6.8653),
    ("Ballon d'Alsace", 47.8222, 6.8406),
    ("La Citadelle de Lille", 50.6403, 3.0444),
    ("Cathédrale Saint-Pierre, Beauvais", 49.4326, 2.0815),
    ("Château de Compiègne", 49.4181, 2.8314),
    ("Nausicaá, Boulogne-sur-Mer", 50.7314, 1.5947),
    ("Les Hortillonnages d'Amiens", 49.8972, 2.3275),
    ("Mémorial de Verdun", 49.1939, 5.4344),
    ("Fort de Douaumont, Verdun", 49.2169, 5.4389),
    # Loire Valley, Centre & Burgundy (91-120)
    ("Château de Chambord", 47.6162, 1.5172),
    ("Château de Chenonceau", 47.3249, 1.0702),
    ("Château de Cheverny", 47.5002, 1.4581),
    ("Château de Blois", 47.5861, 1.3308),
    ("Château d'Amboise", 47.4135, 0.9856),
    ("Château d'Azay-le-Rideau", 47.2590, 0.4658),
    ("Château de Villandry et Jardins", 47.3406, 0.5090),
    ("Cathédrale de Chartres", 48.4472, 1.4878),
    ("Cathédrale de Bourges", 47.0822, 2.3992),
    ("Château d'Angers", 47.4700, -0.5601),
    ("Abbaye Royale de Fontevraud", 47.1811, 0.0514),
    ("Cadre Noir de Saumur", 47.2608, -0.0769),
    ("Palais des Ducs de Bourgogne, Dijon", 47.3217, 5.0417),
    ("Hospices de Beaune", 47.0219, 4.8369),
    ("Abbaye de Cluny", 46.4350, 4.6592),
    ("Basilique de Vézelay", 47.4664, 3.7483),
    ("Site d'Alésia, Alise-Sainte-Reine", 47.5372, 4.4983),
    ("Abbaye de Fontenay, Marmagne", 47.6400, 4.3900),
    ("Roche de Solutré", 46.2975, 4.7183),
    ("Château de Guédelon, Treigny", 47.5833, 3.1556),
    ("Cathédrale de Nevers", 46.9875, 3.1575),
    ("Musée des Beaux-Arts de Dijon", 47.3219, 5.0422),
    ("Château de Sully-sur-Loire", 47.7675, 2.3753),
    ("Maison de Jeanne d'Arc, Orléans", 47.9014, 1.9056),
    ("Cathédrale d'Orléans", 47.9017, 1.9106),
    ("Puy de Dôme", 45.7722, 2.9644),
    ("Vulcain (Volcans d'Auvergne)", 45.8133, 2.9400),
    ("Cathédrale de Clermont-Ferrand", 45.7788, 3.0853),
    ("Basilique de Notre-Dame du Port, Clermont-Ferrand", 45.7806, 3.0897),
    ("L'Aventure Michelin, Clermont-Ferrand", 45.7903, 3.1056),
    # Auvergne-Rhône-Alpes & Alps (121-150)
    ("Basilique Notre-Dame de Fourvière, Lyon",45.7622,4.8226),
    ("Théâtre Antique de Lyon", 45.7597, 4.8197),
    ("Place Bellecour, Lyon", 45.7578, 4.8322),
    ("Parc de la Tête d'Or, Lyon", 45.7786, 4.8547),
    ("Musée des Confluences, Lyon", 45.7328, 4.8181),
    ("Palais de l'Île, Annecy", 45.8988, 6.1261),
    ("Château d'Annecy", 45.8975, 6.1256),
    ("Lac d'Annecy", 45.8500, 6.1667),
    ("Aiguille du Midi, Chamonix", 45.8794, 6.8867),
    ("Mer de Glace, Chamonix", 45.9227, 6.9175),
    ("Bastille de Grenoble", 45.1989, 5.7253),
    ("Palais Idéal du Facteur Cheval, Hauterives", 45.2558, 5.0275),
    ("Gorges de l'Ardèche, Vallon-Pont-d'Arc", 44.3831, 4.4172),
    ("Pont d'Arc, Vallon-Pont-d'Arc", 44.3819, 4.4167),
    ("Monastère royal de Brou, Bourg-en-Bresse", 46.1978, 5.2361),
    ("Lac du Bourget, Aix-les-Bains", 45.7328, 5.8789),
    ("Château de Chambéry", 45.5642, 5.9189),
    ("Parc National de la Vanoise", 45.3333, 6.8333),
    ("Mont Blanc", 45.8325, 6.8647),
    ("Téléphérique de l'Aiguille du Midi", 45.9186, 6.8703),
    ("Via Ferrata de la Clusaz", 45.9056, 6.4250),
    ("Col du Galibier", 45.0642, 6.4078),
    ("Grotte Chauvet 2, Vallon-Pont-d'Arc", 44.4072, 4.4206),
    ("Abbaye de Hautecombe, Saint-Pierre-de-Curtille", 45.7533, 5.8394),
    ("Le Puy-en-Velay - Cathédrale", 45.0456, 3.8847),
    ("Statue Notre-Dame de France, Le Puy-en-Velay", 45.0472, 3.8856),
    ("Puy de Sancy", 45.5292, 2.8156),
    ("Lac Pavin, Besse-et-Saint-Anastaise", 45.4975, 2.8872),
    ("Salins-les-Bains - Grande Saline", 46.9383, 5.8778),
    ("Citadelle de Besançon", 47.2319, 6.0319),
    # Occitanie & Provence-Alpes-Côte d'Azur (151-180)
    ("Cité de Carcassonne", 43.2064, 2.3636),
    ("Pont du Gard, Vers-Pont-du-Gard", 43.9475, 4.5350),
    ("Arènes de Nîmes", 43.8349, 4.3597),
    ("Maison Carrée, Nîmes", 43.8383, 4.3561),
    ("Place du Capitole, Toulouse", 43.6044, 1.4442),
    ("Basilique Saint-Sernin, Toulouse", 43.6083, 1.4419),
    ("Cité de l'Espace, Toulouse", 43.5867, 1.4933),
    ("Cathédrale d'Albi", 43.9286, 2.1428),
    ("Viaduc de Millau", 44.0792, 3.0222),
    ("Gorges du Tarn", 44.3167, 3.3333),
    ("Sanctuaire de Notre-Dame de Lourdes", 43.0975, -0.0583),
    ("Grotte de Massabielle, Lourdes", 43.0976, -0.0585),
    ("Rocamadour - Cité Religieuse", 44.7994, 1.6178),
    ("Pont d'Avignon (Pont Saint-Bénézet)", 43.9547, 4.8047),
    ("Palais des Papes, Avignon", 43.9508, 4.8075),
    ("Amphithéâtre d'Arles", 43.6787, 4.6310),
    ("Parc Naturel Régional de Camargue", 43.5283, 4.4756),
    ("Vieux-Port de Marseille", 43.2953, 5.3744),
    ("Basilique Notre-Dame de la Garde, Marseille", 43.2848, 5.3703),
    ("Château d'If, Marseille", 43.2803, 5.3253),
    ("Mucem, Marseille", 43.2969, 5.3611),
    ("Parc National des Calanques, Marseille", 43.2133, 5.4528),
    ("Palais des Festivals, Cannes", 43.5517, 7.0178),
    ("Promenade des Anglais, Nice", 43.6922, 7.2475),
    ("Colline du Château, Nice", 43.6953, 7.2792),
    ("Vieux Nice", 43.6969, 7.2764),
    ("Musée Matisse, Nice", 43.7194, 7.2761),
    ("Parc National du Mercantour", 44.2000, 7.1500),
    ("Gorges du Verdon, Castellane", 43.7408, 6.3769),
    ("Saint-Tropez - Citadelle", 43.2725, 6.6436),
    # Nouvelle-Aquitaine, Corsica & DOM-TOM (181-200)
    ("Place de la Bourse, Bordeaux", 44.8415, -0.5699),
    ("Miroir d'eau, Bordeaux", 44.8418, -0.5694),
    ("Dune du Pilat, La Teste-de-Buch", 44.5897, -1.2133),
    ("Cité du Vin, Bordeaux", 44.8625, -0.5500),
    ("Rocher de la Vierge, Biarritz", 43.4839, -1.5692),
    ("Aquarium de Biarritz", 43.4836, -1.5678),
    ("Grottes de Lascaux (Lascaux IV), Montignac", 45.0594, 1.1683),
    ("Gouffre de Padirac", 44.8582, 1.7503),
    ("Port de La Rochelle", 46.1583, -1.1528),
    ("Tours de La Rochelle", 46.1558, -1.1553),
    ("Aquarium La Rochelle", 46.1533, -1.1517),
    ("Futuroscope, Chasseneuil-du-Poitou", 46.6698, 0.3697),
    ("Phare des Baleines, Île de Ré", 46.2467, -1.5592),
    ("Citadelle de Bonifacio, Corse", 41.3875, 9.1583),
    ("Calanques de Piana, Corse", 42.2500, 8.6500),
    ("Aiguilles de Bavella, Corse", 41.7956, 9.2247),
    ("Palais des Papes, Carcassonne", 43.2111, 2.3514),
    ("Dune landaise du Pilat", 44.6000, -1.2000),
    ("Château de Pau", 43.2947, -0.3744),
    ("Réserve Naturelle de Scandola, Corse", 42.3667, 8.5667),
]


def seed():
    """Seeds the SQLite database with 200 notable French places linked to user ID 1."""
    app = create_app("development")

    with app.app_context():
        print("Starting seeding process...")

        # 1. Ensure user with ID 1 exists
        owner = UserModel.query.get(1)
        if not owner:
            print("User with ID 1 does not exist. Creating default user...")
            owner = UserModel(
                id=1,
                username="admin",
                email="admin@example.com",
                password_hash="$2b$12$a/f1mi8CW1xqCK2PEYvIcO7URvoGxcvBTW9gqa3Y7m1C.bRvXeVa.",
            )
            db.session.add(owner)
            db.session.commit()
            print("Default User 'admin' (ID: 1) created successfully.")
        else:
            print(
                "User with ID 1 exists. Updating password hash to ensure valid bcrypt format..."
            )
            owner.password_hash = (
                "$2b$12$a/f1mi8CW1xqCK2PEYvIcO7URvoGxcvBTW9gqa3Y7m1C.bRvXeVa."
            )
            db.session.commit()

        # 2. Add places
        places_added = 0
        places_skipped = 0

        for name, lat, lon in NOTABLE_PLACES:
            # Check if place already exists to avoid duplicates
            exists = PlaceModel.query.filter_by(name=name, owner_id=1).first()
            if not exists:
                place = PlaceModel(
                    name=name,
                    latitude=lat,
                    longitude=lon,
                    owner_id=1,
                    visibility="public",
                )
                db.session.add(place)
                places_added += 1
            else:
                places_skipped += 1

        if places_added > 0:
            db.session.commit()

        print("Seeding completed successfully!")
        print(f"Places added: {places_added}")
        print(f"Places skipped (already exists): {places_skipped}")


if __name__ == "__main__":
    seed()
