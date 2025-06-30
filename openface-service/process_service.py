import os
import json
import subprocess
import time
import glob

def process_request(request_file):
    try:
        with open(request_file, 'r') as f:
            request = json.load(f)
        
        print(f"Processing request: {request}")
        
        # Execute OpenFace command
        result = subprocess.run([
            '/home/openface-build/bin/FeatureExtraction',
            '-f', request['input_file'],
            '-out_dir', request['output_dir'],
            '-of', request['output_name'],
            '-gaze', '-aus'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Create completion signal
            completion_file = request_file.replace('.json', '_done.json')
            with open(completion_file, 'w') as f:
                json.dump({'status': 'completed'}, f)
            print(f"Successfully processed: {request_file}")
        else:
            raise Exception(f"OpenFace failed: {result.stderr}")
            
    except Exception as e:
        print(f"Error processing {request_file}: {e}")
        error_file = request_file.replace('.json', '_error.json')
        with open(error_file, 'w') as f:
            json.dump({'status': 'error', 'message': str(e)}, f)
    finally:
        if os.path.exists(request_file):
            os.remove(request_file)

if __name__ == "__main__":
    os.makedirs('/shared_data/requests', exist_ok=True)
    print("OpenFace service started, polling for requests...")
    
    while True:
        try:
            # Look for new request files
            request_files = glob.glob('/shared_data/requests/*.json')
            # Filter out completion and error files
            request_files = [f for f in request_files if not (f.endswith('_done.json') or f.endswith('_error.json'))]
            
            for request_file in request_files:
                process_request(request_file)
            
            time.sleep(1)  # Poll every second
            
        except KeyboardInterrupt:
            print("OpenFace service stopped")
            break
        except Exception as e:
            print(f"Service error: {e}")
            time.sleep(5)
