from fastapi import FastAPI
import endpoints

# Initialize the FastAPI application
app = FastAPI(
    title="Meiji Financial Document API",
    description="API for managing scraped Meiji financial documents.",
    version="1.0.0"
)

# Include the defined API routes
app.include_router(endpoints.router)

@app.get("/")
def read_root():
    """Root endpoint for basic health check."""
    return {"message": "Meiji Financial Document API is running. Check /docs for endpoints."}