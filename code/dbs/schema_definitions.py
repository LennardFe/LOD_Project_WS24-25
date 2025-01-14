# Tables from the Relational Database [Table, [Columns], Label]
TABLES = [
    ("company", ["company_id", "name"], "Company"),
    ("game", ["game_id", "name", "score", "release_date"], "Game"),
    ("genre", ["genre_id", "name"], "Genre"),
    ("genre_type", ["genre_type_id", "name"], "GenreType"),
    ("platform", ["platform_id", "name"], "Platform")
]

# Relationship tables from the Relational Database [Table, [Columns], Table1, Table2, Column, RelationshipType]
RELATIONSHIP_TABLES = [
    ("games_companies", ["game_id", "company_id", "type"], "Game", "Company", "identifier", None),
    ("games_genres", ["game_id", "genre_id"], "Game", "Genre", "identifier", "HAS_GENRE"),
    ("games_platforms", ["game_id", "platform_id"], "Game", "Platform", "identifier", "AVAILABLE_ON"),
]