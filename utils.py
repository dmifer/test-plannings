import os
from pathlib import Path

from dotenv import load_dotenv


# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent

# Read the configuration from .env file
load_dotenv(BASE_DIR / ".env")


PLANNING_PENDING = "Pending for approval"
PLANNING_APPROVED = "Approved"
PLANNING_CHANGE_REQUIRED = "Change required"
PLANNING_DECLINED = "Declined"

INTERNAL_ACTIVITIES = "Internal activities"

APPROVAL_MESSAGES = {
    PLANNING_PENDING: "Approval for planning is required.",
    PLANNING_APPROVED: "Planning approved",
    PLANNING_CHANGE_REQUIRED: "Planning edited approval is required.",
}

# Please don't put your variables directly here,
# instead put them in the `.env` file.

GATE_REDIRECT_LINK = os.getenv("GATE_REDIRECT_LINK", "http://test.com")

# SMTP configuration

HTML_TEMPLATES_SOURCE = os.getenv("HTML_TEMPLATES_SOURCE", "templates")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.office365.com")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_PORT = os.getenv("EMAIL_PORT")

# Database configuration

MONGO_URL = os.getenv("MONGO_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
