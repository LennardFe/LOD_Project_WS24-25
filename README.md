# <div align="justify">Project in WS 24/25 for the module Linked Open Data and Knowledge Graphs in the Master Digital Sciences</div>

Supervisors: **Prof. Dr. Konrad Förstner and Vanessa Scharf**\
Elaboration by: **Ole Berg and Lennard Feuerbach**

<div align="justify">The goal of this project was to visualize data on video games in a knowledge graph form. The video game database MobyGames constitutes the data source for the project. The data on the best-rated 2,500 games was retrieved from <a href="https://www.mobygames.com/info/api">MobyGames’ API</a> and web site. It was first saved in a relational database and then transferred to a <a href="https://neo4j.com">Neo4j</a> graph database. To make the data compliant with the <a href="https://schema.org/">Schema.org</a> vocabulary, a mapping between custom types and types from <a href="https://schema.org/">Schema.org</a> was established. To enable users to utilize the data, a web interface served by a <a href="https://flask.palletsprojects.com/en/stable/">Flask</a> backend was created. Users enter the game of their choice and a serialization format. The stored data is displayed in a structured manner in the desired format. During the final steps of the project, it became clear that the approach of first moving the data into a relational database and then subsequently transferring it to a graph database was not ideal. This process ended up consuming a significant amount of time and additional resources. In future projects, the data structure should be aligned with that of a graph database from the beginning.</div>

---

<div align="justify">Due to financial constraints, the server hosting the web interface could no longer be maintained. However, the code in the repository is enough to reproduce the project, though a new server needs to be set up. To demonstrate how the project, particularly the web interface, looked and functioned, the following provides a walkthrough of the key steps. As an example, the video game <i>Baldur's Gate III</i> will be used.</div>

<p></p>

<div align="justify">As mentioned earlier, the data is initially structured in a relational database format for future use. For the video games, the data is organized as follows.</div>

<br>

<p align="center" width="100%">
    <img width="33%" src="https://github.com/user-attachments/assets/ec67b3e8-68c4-4d43-bd2b-8fbb7068d47e"> 
</p>

<div align="justify">Subsequently, the data is transferred into a graph database structure, as illustrated in the image below.</div>

<br>

![baldur_graph](https://github.com/user-attachments/assets/34a19196-9eb4-481b-a487-4ef0b0a57c90)

<div align="justify">Based on this graph database, the web interface is utilized to retrieve and display the data in various serialization formats. The following image demonstrates the different available options.</div>

<br>

![web_interface](https://github.com/user-attachments/assets/a58b5752-e4f2-4465-9a6a-8005eca9b7f1)

<div align="justify">Based on the user's input in the interface, the data will be displayed in the chosen format. The image afterwards shows the video game data for <i>Baldur's Gate III</i> in the selected Turtle format.</div>

<br>

![baldur_turtle](https://github.com/user-attachments/assets/f2182ba6-8e66-485a-9285-a4680275b131)
