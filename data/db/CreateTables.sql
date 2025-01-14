create table game(game_id int primary key, title varchar, score float, release_date date);
create table genre(genre_id int primary key, genre_type_id int, name varchar);
create table genre_type(genre_type_id int primary key, name varchar);
create table company(company_id int primary key, company_name varchar);
create table game_response(id serial primary key, response jsonb);
create table game_api_response(game_id int primary key, response jsonb);
create table games_genres(game_id int references game(game_id), genre_id int references genre(genre_id), constraint PK_games_genres primary key(game_id, genre_id));
CREATE TYPE company_type AS ENUM ('publisher', 'developer');
create table games_companies(game_id int references game(game_id), company_id int references company(company_id), type company_type, constraint PK_games_companies primary key(game_id, company_id, type));
create table platform(platform_id int primary key, name varchar);
create table games_platforms(game_id int references game(game_id), platform_id int references platform(platform_id), constraint PK_games_platforms primary key (game_id, platform_id));