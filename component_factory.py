#!/usr/bin/env python3
"""
Component Factory for Grasshopper MCP Server
Handles the creation and management of Grasshopper components
"""

import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ParameterType(Enum):
    """Grasshopper parameter types"""
    NUMBER = "Number"
    POINT = "Point"
    VECTOR = "Vector"
    PLANE = "Plane"
    CURVE = "Curve"
    SURFACE = "Surface"
    BREP = "Brep"
    MESH = "Mesh"
    GEOMETRY = "Geometry"
    TEXT = "Text"
    BOOLEAN = "Boolean"
    COLOR = "Color"

@dataclass
class Parameter:
    """Represents a Grasshopper parameter"""
    name: str
    internal_name: str
    param_type: ParameterType
    description: str
    required: bool = False
    default_value: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

@dataclass
class ComponentDefinition:
    """Defines a Grasshopper component"""
    name: str
    internal_name: str
    category: str
    subcategory: str
    description: str
    input_params: List[Parameter]
    output_params: List[Parameter]
    icon_path: Optional[str] = None
    examples: List[str] = None

class ComponentFactory:
    """Factory for creating and managing Grasshopper component definitions"""
    
    def __init__(self):
        self.components: Dict[str, ComponentDefinition] = {}
        self._load_default_components()
    
    def _load_default_components(self):
        """Load default Grasshopper components"""
        
        # Primitive components
        self._add_primitive_components()
        
        # Curve components
        self._add_curve_components()
        
        # Surface components
        self._add_surface_components()
        
        # Transform components
        self._add_transform_components()
        
        # Math components
        self._add_math_components()
        
        logger.info(f"Loaded {len(self.components)} component definitions")
    
    def _add_primitive_components(self):
        """Add primitive geometry components"""
        
        # Point component
        point_comp = ComponentDefinition(
            name="Point",
            internal_name="GH_Point",
            category="Params",
            subcategory="Geometry",
            description="Create a point from X, Y, Z coordinates",
            input_params=[
                Parameter("X", "X", ParameterType.NUMBER, "X coordinate", True, 0.0),
                Parameter("Y", "Y", ParameterType.NUMBER, "Y coordinate", True, 0.0),
                Parameter("Z", "Z", ParameterType.NUMBER, "Z coordinate", True, 0.0)
            ],
            output_params=[
                Parameter("Point", "P", ParameterType.POINT, "Resulting point")
            ],
            examples=[
                "Create a point at origin (0,0,0)",
                "Create a point at coordinates (10, 5, 2)"
            ]
        )
        self.components["point"] = point_comp
        
        # Vector component
        vector_comp = ComponentDefinition(
            name="Vector",
            internal_name="GH_Vector",
            category="Vector",
            subcategory="Vector",
            description="Create a vector from X, Y, Z components",
            input_params=[
                Parameter("X", "X", ParameterType.NUMBER, "X component", True, 0.0),
                Parameter("Y", "Y", ParameterType.NUMBER, "Y component", True, 0.0),
                Parameter("Z", "Z", ParameterType.NUMBER, "Z component", True, 0.0)
            ],
            output_params=[
                Parameter("Vector", "V", ParameterType.VECTOR, "Resulting vector")
            ]
        )
        self.components["vector"] = vector_comp
        
        # Plane component
        plane_comp = ComponentDefinition(
            name="Plane",
            internal_name="GH_Plane",
            category="Vector",
            subcategory="Plane",
            description="Create a plane from origin and normal vector",
            input_params=[
                Parameter("Origin", "O", ParameterType.POINT, "Plane origin", True),
                Parameter("Normal", "N", ParameterType.VECTOR, "Plane normal", False, "Z-axis")
            ],
            output_params=[
                Parameter("Plane", "P", ParameterType.PLANE, "Resulting plane")
            ]
        )
        self.components["plane"] = plane_comp
    
    def _add_curve_components(self):
        """Add curve geometry components"""
        
        # Circle component
        circle_comp = ComponentDefinition(
            name="Circle",
            internal_name="GH_Circle",
            category="Curve",
            subcategory="Primitive",
            description="Create a circle from radius and plane",
            input_params=[
                Parameter("Plane", "P", ParameterType.PLANE, "Base plane", False, "XY plane"),
                Parameter("Radius", "R", ParameterType.NUMBER, "Circle radius", True, 1.0, 0.0)
            ],
            output_params=[
                Parameter("Circle", "C", ParameterType.CURVE, "Resulting circle")
            ],
            examples=[
                "Create a circle with radius 10",
                "Create a circle on XY plane with radius 5"
            ]
        )
        self.components["circle"] = circle_comp
        
        # Line component
        line_comp = ComponentDefinition(
            name="Line",
            internal_name="GH_Line",
            category="Curve",
            subcategory="Primitive",
            description="Create a line between two points",
            input_params=[
                Parameter("Start", "A", ParameterType.POINT, "Start point", True),
                Parameter("End", "B", ParameterType.POINT, "End point", True)
            ],
            output_params=[
                Parameter("Line", "L", ParameterType.CURVE, "Resulting line")
            ],
            examples=[
                "Create a line from origin to point (10,0,0)",
                "Connect two points with a line"
            ]
        )
        self.components["line"] = line_comp
        
        # Rectangle component
        rectangle_comp = ComponentDefinition(
            name="Rectangle",
            internal_name="GH_Rectangle",
            category="Curve",
            subcategory="Primitive",
            description="Create a rectangle from plane and dimensions",
            input_params=[
                Parameter("Plane", "P", ParameterType.PLANE, "Base plane", False, "XY plane"),
                Parameter("X Size", "X", ParameterType.NUMBER, "Size in X direction", True, 1.0, 0.0),
                Parameter("Y Size", "Y", ParameterType.NUMBER, "Size in Y direction", True, 1.0, 0.0)
            ],
            output_params=[
                Parameter("Rectangle", "R", ParameterType.CURVE, "Resulting rectangle")
            ]
        )
        self.components["rectangle"] = rectangle_comp
        
        # Polyline component
        polyline_comp = ComponentDefinition(
            name="Polyline",
            internal_name="GH_Polyline",
            category="Curve",
            subcategory="Spline",
            description="Create a polyline through a series of points",
            input_params=[
                Parameter("Vertices", "V", ParameterType.POINT, "Polyline vertices", True),
                Parameter("Closed", "C", ParameterType.BOOLEAN, "Close polyline", False, False)
            ],
            output_params=[
                Parameter("Polyline", "Pl", ParameterType.CURVE, "Resulting polyline")
            ]
        )
        self.components["polyline"] = polyline_comp
    
    def _add_surface_components(self):
        """Add surface geometry components"""
        
        # Extrude component
        extrude_comp = ComponentDefinition(
            name="Extrude",
            internal_name="GH_Extrude",
            category="Surface",
            subcategory="Freeform",
            description="Extrude a curve or surface along a vector",
            input_params=[
                Parameter("Base", "B", ParameterType.GEOMETRY, "Base geometry to extrude", True),
                Parameter("Direction", "D", ParameterType.VECTOR, "Extrusion direction", True)
            ],
            output_params=[
                Parameter("Extrusion", "E", ParameterType.BREP, "Extruded geometry")
            ],
            examples=[
                "Extrude a circle to create a cylinder",
                "Extrude a rectangle upward by 10 units"
            ]
        )
        self.components["extrude"] = extrude_comp
        
        # Loft component
        loft_comp = ComponentDefinition(
            name="Loft",
            internal_name="GH_Loft",
            category="Surface",
            subcategory="Freeform",
            description="Create a lofted surface through curves",
            input_params=[
                Parameter("Curves", "C", ParameterType.CURVE, "Curves to loft through", True),
                Parameter("Closed", "Cl", ParameterType.BOOLEAN, "Close loft", False, False)
            ],
            output_params=[
                Parameter("Loft", "L", ParameterType.BREP, "Lofted surface")
            ]
        )
        self.components["loft"] = loft_comp
        
        # Revolve component
        revolve_comp = ComponentDefinition(
            name="Revolve",
            internal_name="GH_Revolve",
            category="Surface",
            subcategory="Freeform",
            description="Revolve a curve around an axis",
            input_params=[
                Parameter("Curve", "C", ParameterType.CURVE, "Curve to revolve", True),
                Parameter("Axis", "A", ParameterType.VECTOR, "Axis of revolution", True),
                Parameter("Angle", "An", ParameterType.NUMBER, "Revolution angle in radians", False, 6.28318)  # 2*PI
            ],
            output_params=[
                Parameter("Revolution", "R", ParameterType.BREP, "Revolved surface")
            ]
        )
        self.components["revolve"] = revolve_comp
    
    def _add_transform_components(self):
        """Add transformation components"""
        
        # Move component
        move_comp = ComponentDefinition(
            name="Move",
            internal_name="GH_Move",
            category="Transform",
            subcategory="Euclidean",
            description="Translate geometry along a vector",
            input_params=[
                Parameter("Geometry", "G", ParameterType.GEOMETRY, "Geometry to move", True),
                Parameter("Motion", "T", ParameterType.VECTOR, "Translation vector", True)
            ],
            output_params=[
                Parameter("Geometry", "G", ParameterType.GEOMETRY, "Translated geometry"),
                Parameter("Transform", "X", ParameterType.TEXT, "Transformation data")
            ]
        )
        self.components["move"] = move_comp
        
        # Rotate component
        rotate_comp = ComponentDefinition(
            name="Rotate",
            internal_name="GH_Rotate",
            category="Transform",
            subcategory="Euclidean",
            description="Rotate geometry around an axis",
            input_params=[
                Parameter("Geometry", "G", ParameterType.GEOMETRY, "Geometry to rotate", True),
                Parameter("Angle", "A", ParameterType.NUMBER, "Rotation angle in radians", True),
                Parameter("Axis", "Ax", ParameterType.VECTOR, "Rotation axis", False, "Z-axis"),
                Parameter("Center", "C", ParameterType.POINT, "Center of rotation", False, "Origin")
            ],
            output_params=[
                Parameter("Geometry", "G", ParameterType.GEOMETRY, "Rotated geometry"),
                Parameter("Transform", "X", ParameterType.TEXT, "Transformation data")
            ]
        )
        self.components["rotate"] = rotate_comp
        
        # Scale component
        scale_comp = ComponentDefinition(
            name="Scale",
            internal_name="GH_Scale",
            category="Transform",
            subcategory="Euclidean",
            description="Scale geometry uniformly or non-uniformly",
            input_params=[
                Parameter("Geometry", "G", ParameterType.GEOMETRY, "Geometry to scale", True),
                Parameter("Factor", "F", ParameterType.NUMBER, "Scale factor", True, 1.0),
                Parameter("Center", "C", ParameterType.POINT, "Center of scaling", False, "Origin")
            ],
            output_params=[
                Parameter("Geometry", "G", ParameterType.GEOMETRY, "Scaled geometry"),
                Parameter("Transform", "X", ParameterType.TEXT, "Transformation data")
            ]
        )
        self.components["scale"] = scale_comp
    
    def _add_math_components(self):
        """Add mathematical components"""
        
        # Addition component
        addition_comp = ComponentDefinition(
            name="Addition",
            internal_name="GH_Addition",
            category="Math",
            subcategory="Operators",
            description="Add two numbers",
            input_params=[
                Parameter("A", "A", ParameterType.NUMBER, "First number", True, 0.0),
                Parameter("B", "B", ParameterType.NUMBER, "Second number", True, 0.0)
            ],
            output_params=[
                Parameter("Result", "R", ParameterType.NUMBER, "Sum of A and B")
            ]
        )
        self.components["addition"] = addition_comp
        
        # Multiplication component
        multiplication_comp = ComponentDefinition(
            name="Multiplication",
            internal_name="GH_Multiplication",
            category="Math",
            subcategory="Operators",
            description="Multiply two numbers",
            input_params=[
                Parameter("A", "A", ParameterType.NUMBER, "First number", True, 1.0),
                Parameter("B", "B", ParameterType.NUMBER, "Second number", True, 1.0)
            ],
            output_params=[
                Parameter("Result", "R", ParameterType.NUMBER, "Product of A and B")
            ]
        )
        self.components["multiplication"] = multiplication_comp
        
        # Number Slider component
        slider_comp = ComponentDefinition(
            name="Number Slider",
            internal_name="GH_NumberSlider",
            category="Params",
            subcategory="Input",
            description="A slider for numeric input",
            input_params=[],
            output_params=[
                Parameter("Number", "N", ParameterType.NUMBER, "Slider value")
            ]
        )
        self.components["slider"] = slider_comp
    
    def get_component(self, name: str) -> Optional[ComponentDefinition]:
        """Get component definition by name"""
        return self.components.get(name.lower())
    
    def list_components(self) -> List[str]:
        """List all available component names"""
        return list(self.components.keys())
    
    def get_components_by_category(self, category: str) -> List[ComponentDefinition]:
        """Get all components in a specific category"""
        return [comp for comp in self.components.values() if comp.category.lower() == category.lower()]
    
    def search_components(self, query: str) -> List[ComponentDefinition]:
        """Search components by name or description"""
        query = query.lower()
        results = []
        
        for comp in self.components.values():
            if (query in comp.name.lower() or 
                query in comp.description.lower() or
                any(query in example.lower() for example in (comp.examples or []))):
                results.append(comp)
        
        return results
    
    def get_component_info_for_llm(self) -> str:
        """Get component information formatted for LLM"""
        info = "Available Grasshopper Components:\n\n"
        
        # Group by category
        categories = {}
        for comp in self.components.values():
            if comp.category not in categories:
                categories[comp.category] = []
            categories[comp.category].append(comp)
        
        for category, comps in categories.items():
            info += f"## {category}\n\n"
            for comp in comps:
                info += f"### {comp.name} ({list(self.components.keys())[list(self.components.values()).index(comp)]})\n"
                info += f"{comp.description}\n\n"
                
                if comp.input_params:
                    info += "**Inputs:**\n"
                    for param in comp.input_params:
                        required = " (required)" if param.required else " (optional)"
                        default = f" [default: {param.default_value}]" if param.default_value is not None else ""
                        info += f"- {param.name} ({param.param_type.value}): {param.description}{required}{default}\n"
                    info += "\n"
                
                if comp.output_params:
                    info += "**Outputs:**\n"
                    for param in comp.output_params:
                        info += f"- {param.name} ({param.param_type.value}): {param.description}\n"
                    info += "\n"
                
                if comp.examples:
                    info += "**Examples:**\n"
                    for example in comp.examples:
                        info += f"- {example}\n"
                    info += "\n"
                
                info += "---\n\n"
        
        return info
    
    def validate_component_parameters(self, component_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters for a component"""
        comp = self.get_component(component_name)
        if not comp:
            return {"error": f"Unknown component: {component_name}"}
        
        validated = {}
        errors = []
        
        # Check all input parameters
        for param in comp.input_params:
            if param.name in parameters:
                value = parameters[param.name]
                
                # Type validation (simplified)
                if param.param_type == ParameterType.NUMBER:
                    try:
                        value = float(value)
                        if param.min_value is not None and value < param.min_value:
                            errors.append(f"{param.name} must be >= {param.min_value}")
                        if param.max_value is not None and value > param.max_value:
                            errors.append(f"{param.name} must be <= {param.max_value}")
                    except (ValueError, TypeError):
                        errors.append(f"{param.name} must be a number")
                
                validated[param.name] = value
                
            elif param.required:
                errors.append(f"Required parameter '{param.name}' is missing")
            elif param.default_value is not None:
                validated[param.name] = param.default_value
        
        if errors:
            return {"error": "; ".join(errors)}
        
        return validated
    
    def export_knowledge_base(self, file_path: str):
        """Export component knowledge base to JSON file"""
        data = {}
        for name, comp in self.components.items():
            # Convert ParameterType enum to string
            input_params = []
            for param in comp.input_params:
                param_dict = asdict(param)
                param_dict['param_type'] = param.param_type.value  # Convert enum to string
                input_params.append(param_dict)
            
            output_params = []
            for param in comp.output_params:
                param_dict = asdict(param)
                param_dict['param_type'] = param.param_type.value  # Convert enum to string
                output_params.append(param_dict)
            
            data[name] = {
                "name": comp.name,
                "internal_name": comp.internal_name,
                "category": comp.category,
                "subcategory": comp.subcategory,
                "description": comp.description,
                "input_params": input_params,
                "output_params": output_params,
                "examples": comp.examples or []
            }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported component knowledge base to {file_path}")

def main():
    """Demo of component factory"""
    factory = ComponentFactory()
    
    print("Grasshopper Component Factory")
    print("=" * 40)
    print(f"Loaded {len(factory.components)} components")
    print()
    
    # List all components
    print("Available components:")
    for name in factory.list_components():
        comp = factory.get_component(name)
        print(f"- {comp.name} ({name}): {comp.description}")
    
    print()
    
    # Test component validation
    print("Testing component validation:")
    result = factory.validate_component_parameters("circle", {"Radius": 10.0})
    print(f"Circle with radius 10: {result}")
    
    result = factory.validate_component_parameters("circle", {"Radius": -5.0})
    print(f"Circle with negative radius: {result}")
    
    # Export knowledge base
    factory.export_knowledge_base("/tmp/grasshopper_components.json")
    print("Exported knowledge base to /tmp/grasshopper_components.json")

if __name__ == "__main__":
    main()

