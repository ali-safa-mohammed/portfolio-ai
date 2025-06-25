from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    tech_stack: List[str]
    image_url: str
    demo_url: Optional[str] = None
    github_url: Optional[str] = None
    category: str
    created_date: datetime = Field(default_factory=datetime.utcnow)
    featured: bool = False

class ProjectCreate(BaseModel):
    title: str
    description: str
    tech_stack: List[str]
    image_url: str
    demo_url: Optional[str] = None
    github_url: Optional[str] = None
    category: str
    featured: bool = False

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Project routes
@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects = await db.projects.find().to_list(1000)
    return [Project(**project) for project in projects]

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project)

@api_router.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate):
    project_dict = project.dict()
    project_obj = Project(**project_dict)
    _ = await db.projects.insert_one(project_obj.dict())
    return project_obj

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

@api_router.post("/projects/sample")
async def create_sample_projects():
    # Clear existing projects
    await db.projects.delete_many({})
    
    sample_projects = [
        {
            "title": "AI-Powered Chat Application",
            "description": "A modern chat application with AI integration, real-time messaging, and beautiful UI. Features include smart responses, conversation history, and responsive design.",
            "tech_stack": ["React", "Node.js", "OpenAI", "Socket.io", "MongoDB"],
            "image_url": "https://images.unsplash.com/photo-1587620962725-abab7fe55159?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
            "demo_url": "https://demo-chat.example.com",
            "github_url": "https://github.com/user/ai-chat",
            "category": "Web Application",
            "featured": True
        },
        {
            "title": "3D Portfolio Website",
            "description": "An interactive 3D portfolio showcasing projects with geometric shapes and smooth animations. Built with Three.js and React for an immersive user experience.",
            "tech_stack": ["React", "Three.js", "React Three Fiber", "FastAPI", "MongoDB"],
            "image_url": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
            "demo_url": "https://portfolio-3d.example.com",
            "github_url": "https://github.com/user/3d-portfolio",
            "category": "Portfolio",
            "featured": True
        },
        {
            "title": "E-commerce Platform",
            "description": "Full-stack e-commerce solution with payment integration, inventory management, and admin dashboard. Features modern design and seamless user experience.",
            "tech_stack": ["React", "Express.js", "Stripe", "PostgreSQL", "Redis"],
            "image_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
            "demo_url": "https://shop.example.com",
            "github_url": "https://github.com/user/ecommerce",
            "category": "E-commerce",
            "featured": False
        },
        {
            "title": "Data Visualization Dashboard",
            "description": "Interactive dashboard for data analytics with charts, graphs, and real-time updates. Perfect for business intelligence and data-driven decisions.",
            "tech_stack": ["React", "D3.js", "Python", "FastAPI", "PostgreSQL"],
            "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
            "demo_url": "https://dashboard.example.com",
            "github_url": "https://github.com/user/dashboard",
            "category": "Data Analytics",
            "featured": True
        },
        {
            "title": "Mobile Game Development",
            "description": "Engaging mobile game with 3D graphics, physics simulation, and multiplayer capabilities. Optimized for performance across all devices.",
            "tech_stack": ["Unity", "C#", "Firebase", "Photon", "Blender"],
            "image_url": "https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
            "demo_url": "https://play.google.com/store/apps/details?id=com.example.game",
            "github_url": "https://github.com/user/mobile-game",
            "category": "Game Development",
            "featured": False
        },
        {
            "title": "Blockchain DeFi Platform",
            "description": "Decentralized finance platform with smart contracts, yield farming, and token swapping. Built on Ethereum with modern web3 integration.",
            "tech_stack": ["Solidity", "React", "Web3.js", "Hardhat", "IPFS"],
            "image_url": "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
            "demo_url": "https://defi.example.com",
            "github_url": "https://github.com/user/defi-platform",
            "category": "Blockchain",
            "featured": True
        }
    ]
    
    created_projects = []
    for project_data in sample_projects:
        project_obj = Project(**project_data)
        await db.projects.insert_one(project_obj.dict())
        created_projects.append(project_obj)
    
    return {"message": f"Created {len(created_projects)} sample projects", "projects": created_projects}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()