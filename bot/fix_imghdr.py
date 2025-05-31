#!/usr/bin/env python
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def patch_telegram_bot_api():
    """
    Patch the telegram library to fix imghdr import error in Python 3.13
    """
    try:
        # Get the site-packages directory
        import site
        site_packages = site.getsitepackages()
        
        telegram_found = False
        fixed_any_file = False
        
        for site_dir in site_packages:
            # First check and patch request.py
            request_path = os.path.join(site_dir, 'telegram', 'utils', 'request.py')
            if os.path.exists(request_path):
                logger.info(f"Found Telegram library at: {request_path}")
                telegram_found = True
                
                # Read the file
                with open(request_path, 'r') as file:
                    content = file.read()
                
                # Check if the file contains the problematic import
                if 'import imghdr' in content:
                    logger.info("Found 'import imghdr' in request.py, patching...")
                    
                    # Replace the imghdr import and usage
                    content = content.replace('import imghdr', '# import imghdr')
                    
                    # Replace the imghdr usage with a simple extension check
                    content = content.replace(
                        'imghdr.what(open(image, "rb"))',
                        'os.path.splitext(image)[1][1:].lower() or "jpeg"'
                    )
                    
                    # Write the patched content back
                    with open(request_path, 'w') as file:
                        file.write(content)
                    
                    logger.info("Successfully patched request.py!")
                    fixed_any_file = True
                else:
                    logger.info("The request.py file doesn't contain 'import imghdr' or was already patched.")
            
            # Now check and patch inputfile.py
            inputfile_path = os.path.join(site_dir, 'telegram', 'files', 'inputfile.py')
            if os.path.exists(inputfile_path):
                logger.info(f"Found InputFile module at: {inputfile_path}")
                telegram_found = True
                
                # Read the file
                with open(inputfile_path, 'r') as file:
                    content = file.read()
                
                # Check if the file contains the problematic import
                if 'import imghdr' in content:
                    logger.info("Found 'import imghdr' in inputfile.py, patching...")
                    
                    # Replace the imghdr import
                    content = content.replace('import imghdr', '# import imghdr')
                    
                    # Replace the imghdr usage - may vary depending on how it's used
                    # Here's a common pattern for checking image type
                    content = content.replace(
                        'imghdr.what("", data)',
                        '"jpeg"  # Default to jpeg since imghdr is not available'
                    )
                    
                    content = content.replace(
                        'imghdr.what(self.input_file_content)',
                        '"jpeg"  # Default to jpeg since imghdr is not available'
                    )
                    
                    # Write the patched content back
                    with open(inputfile_path, 'w') as file:
                        file.write(content)
                    
                    logger.info("Successfully patched inputfile.py!")
                    fixed_any_file = True
                else:
                    logger.info("The inputfile.py file doesn't contain 'import imghdr' or was already patched.")
                
            if telegram_found:
                break
        
        if not telegram_found:
            logger.error("Could not find the Telegram library in site-packages.")
            return False
        
        if not fixed_any_file:
            logger.warning("No files needed patching or were already patched.")
        
        return True
    
    except Exception as e:
        logger.error(f"Error patching Telegram library: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting Telegram library patch for Python 3.13")
    if patch_telegram_bot_api():
        logger.info("Patch completed successfully!")
    else:
        logger.error("Failed to apply patch.")
        sys.exit(1) 