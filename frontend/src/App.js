import React, { useEffect, useState, Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, PerspectiveCamera, Environment, Float, Text } from "@react-three/drei";
import axios from "axios";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// 3D Geometric Shape Component
function ProjectShape({ project, position, onClick, isSelected }) {
  const shapeTypes = ['box', 'sphere', 'octahedron', 'tetrahedron', 'cylinder'];
  const shapeIndex = Math.abs(project.title.charCodeAt(0)) % shapeTypes.length;
  const shapeType = shapeTypes[shapeIndex];
  
  const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffd93d', '#6c5ce7'];
  const color = colors[Math.abs(project.title.charCodeAt(1)) % colors.length];

  const renderShape = () => {
    const commonProps = {
      scale: isSelected ? [1.5, 1.5, 1.5] : [1, 1, 1],
      onClick: onClick,
      onPointerOver: (e) => {
        e.stopPropagation();
        document.body.style.cursor = 'pointer';
      },
      onPointerOut: () => {
        document.body.style.cursor = 'auto';
      }
    };

    switch (shapeType) {
      case 'box':
        return (
          <mesh {...commonProps}>
            <boxGeometry args={[1, 1, 1]} />
            <meshStandardMaterial color={color} />
          </mesh>
        );
      case 'sphere':
        return (
          <mesh {...commonProps}>
            <sphereGeometry args={[0.7, 32, 32]} />
            <meshStandardMaterial color={color} />
          </mesh>
        );
      case 'octahedron':
        return (
          <mesh {...commonProps}>
            <octahedronGeometry args={[0.8]} />
            <meshStandardMaterial color={color} />
          </mesh>
        );
      case 'tetrahedron':
        return (
          <mesh {...commonProps}>
            <tetrahedronGeometry args={[0.9]} />
            <meshStandardMaterial color={color} />
          </mesh>
        );
      case 'cylinder':
        return (
          <mesh {...commonProps}>
            <cylinderGeometry args={[0.6, 0.6, 1.2, 8]} />
            <meshStandardMaterial color={color} />
          </mesh>
        );
      default:
        return (
          <mesh {...commonProps}>
            <boxGeometry args={[1, 1, 1]} />
            <meshStandardMaterial color={color} />
          </mesh>
        );
    }
  };

  return (
    <Float
      position={position}
      rotationIntensity={isSelected ? 2 : 1}
      floatIntensity={isSelected ? 2 : 1}
      speed={isSelected ? 3 : 1}
    >
      {renderShape()}
      {isSelected && (
        <Text
          position={[0, -2, 0]}
          fontSize={0.3}
          color="white"
          anchorX="center"
          anchorY="middle"
          maxWidth={4}
        >
          {project.title}
        </Text>
      )}
    </Float>
  );
}

// 3D Scene Component
function Scene({ projects, selectedProject, onProjectClick }) {
  // Arrange projects in a circular pattern
  const radius = 8;
  const positions = projects.map((_, index) => {
    const angle = (index / projects.length) * Math.PI * 2;
    const x = Math.cos(angle) * radius;
    const z = Math.sin(angle) * radius;
    const y = (Math.random() - 0.5) * 4; // Random height variation
    return [x, y, z];
  });

  return (
    <>
      <PerspectiveCamera makeDefault position={[0, 0, 15]} />
      <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
      <Environment preset="sunset" />
      
      {/* Ambient lighting */}
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <pointLight position={[-10, -10, -5]} intensity={0.5} />
      
      {/* Render project shapes */}
      {projects.map((project, index) => (
        <ProjectShape
          key={project.id}
          project={project}
          position={positions[index]}
          onClick={() => onProjectClick(project)}
          isSelected={selectedProject?.id === project.id}
        />
      ))}
      
      {/* Background particles */}
      <Stars />
    </>
  );
}

// Star particles component
function Stars() {
  const starPositions = [];
  for (let i = 0; i < 200; i++) {
    starPositions.push([
      (Math.random() - 0.5) * 50,
      (Math.random() - 0.5) * 50,
      (Math.random() - 0.5) * 50
    ]);
  }

  return (
    <group>
      {starPositions.map((position, index) => (
        <mesh key={index} position={position}>
          <sphereGeometry args={[0.02, 8, 8]} />
          <meshBasicMaterial color="white" />
        </mesh>
      ))}
    </group>
  );
}

// Project Details Panel
function ProjectPanel({ project, onClose }) {
  if (!project) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-2xl font-bold text-gray-800">{project.title}</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
            >
              ×
            </button>
          </div>
          
          <img
            src={project.image_url}
            alt={project.title}
            className="w-full h-48 object-cover rounded-lg mb-4"
          />
          
          <div className="mb-4">
            <span className="inline-block bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
              {project.category}
            </span>
            {project.featured && (
              <span className="inline-block bg-yellow-100 text-yellow-800 text-sm px-3 py-1 rounded-full ml-2">
                Featured
              </span>
            )}
          </div>
          
          <p className="text-gray-600 mb-4">{project.description}</p>
          
          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-2">Tech Stack</h3>
            <div className="flex flex-wrap gap-2">
              {project.tech_stack.map((tech, index) => (
                <span
                  key={index}
                  className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>
          
          <div className="flex gap-4">
            {project.demo_url && (
              <a
                href={project.demo_url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
              >
                Live Demo
              </a>
            )}
            {project.github_url && (
              <a
                href={project.github_url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-gray-800 text-white px-4 py-2 rounded-lg hover:bg-gray-900 transition-colors"
              >
                View Code
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Loading Component
function LoadingScreen() {
  return (
    <div className="fixed inset-0 bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white mb-4"></div>
        <p className="text-white text-xl">Loading 3D Portfolio...</p>
      </div>
    </div>
  );
}

// Main App Component
function App() {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      
      // First, create sample projects
      await axios.post(`${API}/projects/sample`);
      
      // Then, fetch all projects
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
      setError(null);
    } catch (error) {
      console.error('Error loading projects:', error);
      setError('Failed to load projects. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleProjectClick = (project) => {
    setSelectedProject(project);
  };

  const closeProjectPanel = () => {
    setSelectedProject(null);
  };

  if (loading) {
    return <LoadingScreen />;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-900 via-red-800 to-red-700 flex items-center justify-center">
        <div className="text-center text-white">
          <h1 className="text-4xl font-bold mb-4">Error</h1>
          <p className="text-xl mb-4">{error}</p>
          <button
            onClick={loadProjects}
            className="bg-white text-red-800 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 relative overflow-hidden">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-10 p-6">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-2">
            3D Portfolio
          </h1>
          <p className="text-lg md:text-xl text-gray-300">
            Explore my projects in an interactive 3D space
          </p>
        </div>
      </div>

      {/* Instructions */}
      <div className="absolute bottom-0 left-0 right-0 z-10 p-6">
        <div className="text-center text-white">
          <p className="text-sm md:text-base opacity-75">
            Click and drag to rotate • Scroll to zoom • Click on shapes to view project details
          </p>
        </div>
      </div>

      {/* 3D Canvas */}
      <Canvas className="w-full h-full">
        <Suspense fallback={null}>
          <Scene
            projects={projects}
            selectedProject={selectedProject}
            onProjectClick={handleProjectClick}
          />
        </Suspense>
      </Canvas>

      {/* Project Details Panel */}
      <ProjectPanel
        project={selectedProject}
        onClose={closeProjectPanel}
      />
    </div>
  );
}

export default App;