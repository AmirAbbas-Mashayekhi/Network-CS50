# CS50W Network Project

Welcome to the **CS50 Web Programming (CS50W)** course's **Network** project, developed as a social network application using **Django** with a **MySQL** database. This project is **dockerized** for easy setup and execution.

---

## 📋 Requirements

- **Python 3.x**
- **Django**
- **MySQL**
- **Docker** (for containerization)

---

## 🚀 Getting Started

1. Clone this repository:

```bash
git clone https://github.com/AmirAbbas-Mashayekhi/Network-CS50.git
cd network
```

2. **Docker Setup**:  
   Ensure **Docker** is installed on your system. Then, build and run the Docker containers with the following command:

```bash
docker-compose up --build
```

This will create and start the containers. You can access the application at `http://localhost:8000`.

---

## 🗄️ Setup the Database

1. Once the containers are running, apply migrations to your MySQL database by running:

```bash
docker-compose exec web python manage.py makemigrations network
docker-compose exec web python manage.py migrate
```

This will set up the initial database schema.

---

## 🖥️ Running the Application

1. The server is already running inside the Docker container, but if needed, you can manually start it:

```bash
docker-compose exec web python manage.py runserver
```

2. Open your browser and navigate to `http://localhost:8000`.

3. Register an account and start exploring the application!

---

## 📂 Project Structure

- **network**: The main app of the Django project, containing views, models, templates, and URLs for user registration, posts, following, and liking.
- **Docker**: The project is containerized using `docker-compose` for the web and database services, ensuring a consistent environment.

---

## 🌟 Features

- **User Authentication**:

  - Users can **register**, **log in**, and **log out**.
  - Once logged in, users can view their profile and make posts.

- **New Post**:

  - Signed-in users can create new **text-based posts**.
  - Posts are displayed on the **All Posts** page, sorted by most recent.

- **User Profile Page**:

  - Displays the number of **followers** and **following**.
  - Shows all posts from the user, sorted in reverse chronological order.
  - Allows users to **follow** or **unfollow** others.

- **Following**:

  - The **Following** page shows posts from the users the current user is following.
  - Pagination is implemented (10 posts per page).

- **Edit Post**:

  - Users can **edit** their own posts without reloading the page.
  - JavaScript is used to handle post editing asynchronously.

- **Like/Unlike Post**:

  - Users can **like** or **unlike** posts asynchronously.
  - The like count updates dynamically without refreshing the page.

- **Pagination**:
  - Posts are paginated (10 posts per page).

---

## 🛠️ Troubleshooting

- If you run into issues with Docker, try:

  ```bash
  docker-compose down
  docker-compose up --build
  ```

- To clear all containers and start fresh, use:

  ```bash
  docker-compose down --volumes --remove-orphans
  ```

---

## ⚙️ Technologies Used

- ![Django](https://img.shields.io/badge/Django-5.1.3-brightgreen)
- ![MySQL](https://img.shields.io/badge/MySQL-8.0-blue)
- ![Docker](https://img.shields.io/badge/Docker-27.3-blueviolet)
- ![Python](https://img.shields.io/badge/Python-3.10-blue)

---

## 💡 Acknowledgments

This project is part of the **CS50W** course from **Harvard University** . It was built using Django, MySQL, and Docker as part of the **Network** project, focusing on building a social network with user authentication, post creation, following users, liking posts, and other essential social media features.
