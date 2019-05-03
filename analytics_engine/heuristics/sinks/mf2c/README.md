#Web API Documentation

Analytics Engine provides following Web API Endpoints

- **optimal**

		POST /mf2c/optimal

	optimal endpoint returns a list of all the agents (devices) currently active in the landscape, together with the current resource utilization. Optionally, the list can be filtered for a specific device. Below is an example of json body for making a POST request to optimal.
	
		{
			    "name": "clearwater_ims",
			    "device_id": "092b7908-69ee-46ee-b2c7-2d9ae23ee298", 
			    'sort_order': ['memory', 'cpu'], 
			    'telemetry_filter': False, 
			    "project": "mf2c"
		}  

	**Inputs**:
	-- *name* : Mandatory - Any string value
	-- *device_id* : Optional. Device to be filtered for. No device filtering applied if this value is not provided. Invalid device will return 404 error.
	-- *sort_order* : Optional. Any array specifiying the sort order for the output. Valid values - 'cpu', 'memory', 'network', 'disk'. Default - ['cpu']. Output will be sorted in the ascending order of the utilization level of the resources specified.
	-- *telemetry_filter* : Optional. Flag to indicate if devices that do not have telemetry data should be removed from the list.  Default - False. 
	-- *project* : Required if device_id is provided for filtering. Otherwise not required.


	**Output**:
	
	Output is JSON with below fields.
	
		[
			{
				'ipaddress': '172.18.0.19', 
				'mf2c_device_id': '6550f9fa-eb73-446f-acb3-f12f86524e49', 
				'network utilization': 0.02, 
				'compute saturation': 0.00, 
				'node_name': 'IRILD039', 
				'disk utilization': .21, 
				'compute utilization': .32, 
				'memory saturation': 0.00, 
				'type': 'machine', 
				'memory utilization': .51, 
				'network saturation': 0.00, 
				'disk saturation': 0.00
			}
		]

	NOTES : 
		- Utilization numbers are percent values and not absolute values. A value of 0.21 indicates 21%.
		- Saturation calculations are yet to be implemented.

- **analyse**

		POST /mf2c/analyse

	analyse endpoint runs an analysis of telemetry data of a service for the requested timeframe. 


- refine

		POST /mf2c/refine

refine endpoint uses an analysis previously performed by a call to analyse end point and updates the service in CIMI with recommended CPU, Memory, Disk & Network requirements for a service. 

Example web API calls are in the [test_client](../../../../test_client) folder.

	optimal - [/analytics_engine/test_client/rest_api_client.py](../../../../test_client/rest_api_client.py)

	analyse - [/analytics_engine/test_client/rest_api_client_analyse.py](../../../../test_client/rest_api_client_analyse.py)

	refine - [/analytics_engine/test_client/rest_api_client_refine.py](../../../../test_client/rest_api_client_refine.py)


