#!/usr/bin/env python3
import requests
import json
import uuid
import time
import sys
from typing import Dict, Any, List, Optional

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://319e625e-1b32-431c-ab95-9fe03fae0f37.preview.emergentagent.com/api"

def print_test_header(test_name: str) -> None:
    """Print a formatted test header."""
    print(f"\n{'=' * 80}")
    print(f"TEST: {test_name}")
    print(f"{'=' * 80}")

def print_response(response: requests.Response) -> None:
    """Print formatted response details."""
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    try:
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response Body: {response.text}")

def test_api_health() -> bool:
    """Test the API health check endpoint."""
    print_test_header("API Health Check")
    
    try:
        response = requests.get(f"{BACKEND_URL}/")
        print_response(response)
        
        if response.status_code == 200 and "message" in response.json():
            print("✅ API health check passed")
            return True
        else:
            print("❌ API health check failed")
            return False
    except Exception as e:
        print(f"❌ API health check failed with exception: {str(e)}")
        return False

def test_cors() -> bool:
    """Test CORS configuration."""
    print_test_header("CORS Configuration")
    
    try:
        # Send an OPTIONS request to check CORS headers
        response = requests.options(f"{BACKEND_URL}/", 
                                   headers={
                                       "Origin": "http://example.com",
                                       "Access-Control-Request-Method": "GET",
                                       "Access-Control-Request-Headers": "Content-Type"
                                   })
        print_response(response)
        
        # Check if CORS headers are present
        if (response.status_code == 200 and 
            "access-control-allow-origin" in response.headers and 
            "access-control-allow-methods" in response.headers):
            print("✅ CORS configuration passed")
            return True
        else:
            print("❌ CORS configuration failed")
            return False
    except Exception as e:
        print(f"❌ CORS test failed with exception: {str(e)}")
        return False

def test_create_sample_projects() -> bool:
    """Test creating sample projects."""
    print_test_header("Create Sample Projects")
    
    try:
        response = requests.post(f"{BACKEND_URL}/projects/sample")
        print_response(response)
        
        if response.status_code == 200 and "projects" in response.json():
            projects = response.json()["projects"]
            if len(projects) == 6:  # Expecting 6 sample projects
                print(f"✅ Sample projects created successfully: {len(projects)} projects")
                
                # Validate project structure
                categories = set()
                for project in projects:
                    categories.add(project["category"])
                    
                    # Check required fields
                    required_fields = ["id", "title", "description", "tech_stack", 
                                      "image_url", "category", "created_date"]
                    for field in required_fields:
                        if field not in project:
                            print(f"❌ Project missing required field: {field}")
                            return False
                
                print(f"✅ Project categories found: {categories}")
                expected_categories = {"Web Application", "Portfolio", "E-commerce", 
                                      "Data Analytics", "Game Development", "Blockchain"}
                if categories == expected_categories:
                    print("✅ All expected categories present")
                else:
                    print(f"⚠️ Missing categories: {expected_categories - categories}")
                
                return True
            else:
                print(f"❌ Expected 6 sample projects, got {len(projects)}")
                return False
        else:
            print("❌ Failed to create sample projects")
            return False
    except Exception as e:
        print(f"❌ Sample projects creation failed with exception: {str(e)}")
        return False

def test_get_all_projects() -> Optional[List[Dict[str, Any]]]:
    """Test fetching all projects."""
    print_test_header("Get All Projects")
    
    try:
        response = requests.get(f"{BACKEND_URL}/projects")
        print_response(response)
        
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ Retrieved {len(projects)} projects")
            return projects
        else:
            print("❌ Failed to retrieve projects")
            return None
    except Exception as e:
        print(f"❌ Get all projects failed with exception: {str(e)}")
        return None

def test_get_project_by_id(project_id: str) -> bool:
    """Test fetching a specific project by ID."""
    print_test_header(f"Get Project by ID: {project_id}")
    
    try:
        response = requests.get(f"{BACKEND_URL}/projects/{project_id}")
        print_response(response)
        
        if response.status_code == 200 and "id" in response.json():
            project = response.json()
            if project["id"] == project_id:
                print(f"✅ Successfully retrieved project: {project['title']}")
                return True
            else:
                print(f"❌ Retrieved wrong project. Expected ID {project_id}, got {project['id']}")
                return False
        else:
            print(f"❌ Failed to retrieve project with ID {project_id}")
            return False
    except Exception as e:
        print(f"❌ Get project by ID failed with exception: {str(e)}")
        return False

def test_create_project() -> Optional[str]:
    """Test creating a new project."""
    print_test_header("Create New Project")
    
    new_project = {
        "title": "Test Project",
        "description": "This is a test project created by the automated test script",
        "tech_stack": ["Python", "FastAPI", "Testing"],
        "image_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97",
        "demo_url": "https://test.example.com",
        "github_url": "https://github.com/user/test-project",
        "category": "Testing",
        "featured": True
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/projects",
            json=new_project
        )
        print_response(response)
        
        if response.status_code == 200 and "id" in response.json():
            project_id = response.json()["id"]
            print(f"✅ Successfully created project with ID: {project_id}")
            return project_id
        else:
            print("❌ Failed to create new project")
            return None
    except Exception as e:
        print(f"❌ Create project failed with exception: {str(e)}")
        return None

def test_delete_project(project_id: str) -> bool:
    """Test deleting a project."""
    print_test_header(f"Delete Project: {project_id}")
    
    try:
        response = requests.delete(f"{BACKEND_URL}/projects/{project_id}")
        print_response(response)
        
        if response.status_code == 200:
            print(f"✅ Successfully deleted project with ID: {project_id}")
            
            # Verify the project is actually deleted
            verify_response = requests.get(f"{BACKEND_URL}/projects/{project_id}")
            if verify_response.status_code == 404:
                print("✅ Verified project was deleted (404 Not Found)")
                return True
            else:
                print(f"❌ Project still exists after deletion, status: {verify_response.status_code}")
                return False
        else:
            print(f"❌ Failed to delete project with ID {project_id}")
            return False
    except Exception as e:
        print(f"❌ Delete project failed with exception: {str(e)}")
        return False

def test_delete_nonexistent_project() -> bool:
    """Test deleting a non-existent project."""
    print_test_header("Delete Non-existent Project")
    
    fake_id = str(uuid.uuid4())
    try:
        response = requests.delete(f"{BACKEND_URL}/projects/{fake_id}")
        print_response(response)
        
        if response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent project")
            return True
        else:
            print(f"❌ Expected 404, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Delete non-existent project test failed with exception: {str(e)}")
        return False

def run_all_tests():
    """Run all API tests in sequence."""
    print("\n🔍 Starting Backend API Tests 🔍\n")
    
    test_results = {}
    
    # Test 1: API Health Check
    test_results["API Health Check"] = test_api_health()
    
    # Test 2: CORS Configuration
    test_results["CORS Configuration"] = test_cors()
    
    # Test 3: Create Sample Projects
    test_results["Create Sample Projects"] = test_create_sample_projects()
    
    # Test 4: Get All Projects
    projects = test_get_all_projects()
    test_results["Get All Projects"] = projects is not None and len(projects) > 0
    
    # Test 5: Get Project by ID (if we have projects)
    if projects and len(projects) > 0:
        project_id = projects[0]["id"]
        test_results["Get Project by ID"] = test_get_project_by_id(project_id)
    else:
        test_results["Get Project by ID"] = False
        print("❌ Skipping Get Project by ID test as no projects were retrieved")
    
    # Test 6: Create New Project
    new_project_id = test_create_project()
    test_results["Create New Project"] = new_project_id is not None
    
    # Test 7: Delete Project (if we created one)
    if new_project_id:
        test_results["Delete Project"] = test_delete_project(new_project_id)
    else:
        test_results["Delete Project"] = False
        print("❌ Skipping Delete Project test as no project was created")
    
    # Test 8: Delete Non-existent Project
    test_results["Delete Non-existent Project"] = test_delete_nonexistent_project()
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        if not result:
            all_passed = False
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 All tests passed! 🎉")
    else:
        print("❌ Some tests failed. See details above.")
    print("=" * 80 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)