from app import routes  # Import routes (which also initializes the app)

if __name__ == "__main__":
    routes.app.run(debug=True)  # Run the app from the routes module