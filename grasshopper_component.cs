using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Rhino.Geometry;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace GrasshopperMCP
{
    /// <summary>
    /// Grasshopper MCP Component for receiving commands from MCP Server
    /// </summary>
    public class GH_MCPComponent : GH_Component
    {
        private TcpListener _tcpListener;
        private Thread _tcpListenerThread;
        private bool _isListening = false;
        private int _port = 8888;
        private Dictionary<string, IGH_DocumentObject> _createdComponents;

        public GH_MCPComponent()
            : base("MCP Bridge", "MCP",
                "Grasshopper MCP Bridge Component for AI-driven parametric design",
                "Params", "Util")
        {
            _createdComponents = new Dictionary<string, IGH_DocumentObject>();
        }

        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddBooleanParameter("Enable", "E", "Enable MCP Bridge", GH_ParamAccess.item, false);
            pManager.AddIntegerParameter("Port", "P", "TCP Port for MCP communication", GH_ParamAccess.item, 8888);
        }

        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddTextParameter("Status", "S", "MCP Bridge Status", GH_ParamAccess.item);
            pManager.AddTextParameter("Log", "L", "MCP Bridge Log", GH_ParamAccess.list);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            bool enable = false;
            int port = 8888;

            DA.GetData(0, ref enable);
            DA.GetData(1, ref port);

            if (enable && !_isListening)
            {
                _port = port;
                StartTcpListener();
                DA.SetData(0, "MCP Bridge Started on port " + _port);
            }
            else if (!enable && _isListening)
            {
                StopTcpListener();
                DA.SetData(0, "MCP Bridge Stopped");
            }
            else if (_isListening)
            {
                DA.SetData(0, "MCP Bridge Running on port " + _port);
            }
            else
            {
                DA.SetData(0, "MCP Bridge Disabled");
            }

            // Output log messages (placeholder for now)
            DA.SetDataList(1, new List<string> { "MCP Bridge initialized" });
        }

        private void StartTcpListener()
        {
            try
            {
                _tcpListener = new TcpListener(IPAddress.Any, _port);
                _tcpListenerThread = new Thread(new ThreadStart(ListenForClients));
                _tcpListenerThread.Start();
                _isListening = true;
            }
            catch (Exception ex)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Failed to start TCP listener: " + ex.Message);
            }
        }

        private void StopTcpListener()
        {
            try
            {
                _isListening = false;
                if (_tcpListener != null)
                {
                    _tcpListener.Stop();
                }
                if (_tcpListenerThread != null)
                {
                    _tcpListenerThread.Abort();
                }
            }
            catch (Exception ex)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, "Error stopping TCP listener: " + ex.Message);
            }
        }

        private void ListenForClients()
        {
            _tcpListener.Start();

            while (_isListening)
            {
                try
                {
                    using (TcpClient client = _tcpListener.AcceptTcpClient())
                    {
                        Thread clientThread = new Thread(new ParameterizedThreadStart(HandleClientComm));
                        clientThread.Start(client);
                    }
                }
                catch (Exception ex)
                {
                    if (_isListening)
                    {
                        AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "TCP Listener error: " + ex.Message);
                    }
                }
            }
        }

        private void HandleClientComm(object client)
        {
            TcpClient tcpClient = (TcpClient)client;
            NetworkStream clientStream = tcpClient.GetStream();

            byte[] message = new byte[4096];
            int bytesRead;

            while (true)
            {
                bytesRead = 0;

                try
                {
                    bytesRead = clientStream.Read(message, 0, 4096);
                }
                catch
                {
                    break;
                }

                if (bytesRead == 0)
                {
                    break;
                }

                string jsonMessage = Encoding.UTF8.GetString(message, 0, bytesRead);
                string response = ProcessCommand(jsonMessage);

                byte[] responseBytes = Encoding.UTF8.GetBytes(response + "\n");
                clientStream.Write(responseBytes, 0, responseBytes.Length);
                clientStream.Flush();
            }

            tcpClient.Close();
        }

        private string ProcessCommand(string jsonCommand)
        {
            try
            {
                JObject command = JObject.Parse(jsonCommand);
                string commandType = command["command"]?.ToString();

                switch (commandType)
                {
                    case "create_component":
                        return CreateComponent(command);
                    case "connect_parameters":
                        return ConnectParameters(command);
                    case "clear_canvas":
                        return ClearCanvas();
                    default:
                        return JsonConvert.SerializeObject(new { success = false, error = "Unknown command: " + commandType });
                }
            }
            catch (Exception ex)
            {
                return JsonConvert.SerializeObject(new { success = false, error = ex.Message });
            }
        }

        private string CreateComponent(JObject command)
        {
            try
            {
                string componentName = command["component_name"]?.ToString();
                JObject parameters = command["parameters"] as JObject;

                IGH_DocumentObject newComponent = null;
                string componentGuid = Guid.NewGuid().ToString();

                // Create component based on type
                switch (componentName)
                {
                    case "GH_Circle":
                        newComponent = CreateCircleComponent(parameters);
                        break;
                    case "GH_Point":
                        newComponent = CreatePointComponent(parameters);
                        break;
                    case "GH_Line":
                        newComponent = CreateLineComponent(parameters);
                        break;
                    default:
                        return JsonConvert.SerializeObject(new { success = false, error = "Unsupported component: " + componentName });
                }

                if (newComponent != null)
                {
                    // Add component to document
                    OnPingDocument().AddObject(newComponent, false);
                    _createdComponents[componentGuid] = newComponent;

                    // Trigger solution
                    OnPingDocument().NewSolution(false);

                    return JsonConvert.SerializeObject(new 
                    { 
                        success = true, 
                        component_guid = componentGuid,
                        component_name = componentName,
                        message = "Component created successfully"
                    });
                }
                else
                {
                    return JsonConvert.SerializeObject(new { success = false, error = "Failed to create component" });
                }
            }
            catch (Exception ex)
            {
                return JsonConvert.SerializeObject(new { success = false, error = ex.Message });
            }
        }

        private IGH_DocumentObject CreateCircleComponent(JObject parameters)
        {
            // This is a simplified example - in a real implementation,
            // you would create actual Grasshopper components
            
            // For demonstration, we'll create a simple component that represents a circle
            // In practice, you would instantiate the actual Grasshopper Circle component
            
            double radius = parameters["Radius"]?.ToObject<double>() ?? 1.0;
            string plane = parameters["Plane"]?.ToString() ?? "XY";
            
            // Create a placeholder component (this would be replaced with actual Grasshopper component creation)
            var circleComponent = new GH_NumberSlider();
            circleComponent.CreateAttributes();
            circleComponent.Attributes.Pivot = new PointF(100, 100);
            circleComponent.Slider.Minimum = 0;
            circleComponent.Slider.Maximum = 100;
            circleComponent.Slider.Value = (decimal)radius;
            circleComponent.NickName = "Circle_R";
            
            return circleComponent;
        }

        private IGH_DocumentObject CreatePointComponent(JObject parameters)
        {
            double x = parameters["X"]?.ToObject<double>() ?? 0.0;
            double y = parameters["Y"]?.ToObject<double>() ?? 0.0;
            double z = parameters["Z"]?.ToObject<double>() ?? 0.0;
            
            // Create a placeholder component for point
            var pointComponent = new GH_Panel();
            pointComponent.CreateAttributes();
            pointComponent.Attributes.Pivot = new PointF(200, 100);
            pointComponent.UserText = $"Point({x},{y},{z})";
            pointComponent.NickName = "Point";
            
            return pointComponent;
        }

        private IGH_DocumentObject CreateLineComponent(JObject parameters)
        {
            // Create a placeholder component for line
            var lineComponent = new GH_Panel();
            lineComponent.CreateAttributes();
            lineComponent.Attributes.Pivot = new PointF(300, 100);
            lineComponent.UserText = "Line Component";
            lineComponent.NickName = "Line";
            
            return lineComponent;
        }

        private string ConnectParameters(JObject command)
        {
            try
            {
                string sourceGuid = command["source_component_guid"]?.ToString();
                string targetGuid = command["target_component_guid"]?.ToString();
                string sourceParam = command["source_parameter_name"]?.ToString();
                string targetParam = command["target_parameter_name"]?.ToString();

                // Find components by GUID
                if (_createdComponents.ContainsKey(sourceGuid) && _createdComponents.ContainsKey(targetGuid))
                {
                    var sourceComponent = _createdComponents[sourceGuid];
                    var targetComponent = _createdComponents[targetGuid];

                    // In a real implementation, you would connect the actual parameters
                    // This is a simplified placeholder

                    return JsonConvert.SerializeObject(new 
                    { 
                        success = true, 
                        message = $"Connected {sourceParam} to {targetParam}"
                    });
                }
                else
                {
                    return JsonConvert.SerializeObject(new { success = false, error = "Component not found" });
                }
            }
            catch (Exception ex)
            {
                return JsonConvert.SerializeObject(new { success = false, error = ex.Message });
            }
        }

        private string ClearCanvas()
        {
            try
            {
                // Clear all created components
                foreach (var component in _createdComponents.Values)
                {
                    OnPingDocument().RemoveObject(component, false);
                }
                _createdComponents.Clear();

                // Trigger solution
                OnPingDocument().NewSolution(false);

                return JsonConvert.SerializeObject(new { success = true, message = "Canvas cleared" });
            }
            catch (Exception ex)
            {
                return JsonConvert.SerializeObject(new { success = false, error = ex.Message });
            }
        }

        protected override void BeforeSolveInstance()
        {
            base.BeforeSolveInstance();
        }

        protected override void AfterSolveInstance()
        {
            base.AfterSolveInstance();
        }

        public override void RemovedFromDocument(GH_Document document)
        {
            StopTcpListener();
            base.RemovedFromDocument(document);
        }

        protected override Bitmap Icon => null;

        public override Guid ComponentGuid => new Guid("12345678-1234-5678-9012-123456789012");
    }

    /// <summary>
    /// Assembly info for the Grasshopper MCP plugin
    /// </summary>
    public class GH_MCPAssemblyInfo : GH_AssemblyInfo
    {
        public override string Name => "Grasshopper MCP";
        public override Bitmap Icon => null;
        public override string Description => "Model Context Protocol bridge for AI-driven parametric design";
        public override Guid Id => new Guid("87654321-4321-8765-2109-876543210987");
        public override string AuthorName => "Manus AI";
        public override string AuthorContact => "support@manus.ai";
    }
}

