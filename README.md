# Uplink – Social Activity Matching Platform

**Uplink** is a platform designed to help users discover and join social activities that match their interests. By connecting people with similar preferences, the platform makes it easy to find events and build meaningful social connections.

**Technologies:**
- **Backend:** FastAPI
- **Database:** PostgreSQL

## Backend Architecture

- **core/** – Settings, database configuration, and AI model setup  
- **models/** – SQLAlchemy entities representing database tables  
- **schemas/** – Pydantic models for validating request and response data  
- **routers/** – API endpoints for users, authentication, and activities  
- **services/** – Business logic  

## Recommender System

Uplink uses **sentence-transformers** (model `all-MiniLM-L6-v2`) to convert user interests and activity tags into embeddings. The recommendation system works by comparing user interests with activity tags using **cosine similarity** and then selecting the top 5 activities with the highest similarity scores to present to the user.

## API Endpoints

### Users
- `POST /users` – Create a new user
- `GET /users` – List all users (supports `skip` and `limit` query parameters)
- `GET /users/id/{user_id}` – Get user by ID
- `GET /users/{username}` – Get user by username
- `PUT /users/{user_id}` – Update user profile
- `DELETE /users/{user_id}` – Delete user profile

### Authentication
- `POST /auth/register` – Register a new account
- `POST /auth/login` – Login and obtain JWT token
- `GET /auth/me` – Get current logged-in user profile
- `POST /auth/refresh` – Refresh JWT token

### Activities
- `POST /activities` – Create a new activity
- `GET /activities` – List activities (supports `skip` and `limit` query parameters)
- `GET /activities/{activity_id}` – Get activity details by ID
- `PUT /activities/{activity_id}` – Update an activity
- `DELETE /activities/{activity_id}` – Delete an activity

### Activity Participation
- `POST /activities/{activity_id}/join` – Join an activity
- `DELETE /activities/{activity_id}/leave` – Leave an activity
- `GET /activities/me/hosted` – List activities hosted by the current user
- `GET /activities/me/joined` – List activities the current user has joined

### Recommendations
- `GET /activities/me/recommend` – Get personalized activity recommendations (supports `limit` query parameter)

### Health
- `GET /health` – Health check endpoint

## Try the API

You can explore and test the API using the interactive documentation here:  
[Uplink API Documentation](https://uplink-6o9j.onrender.com/docs)  
