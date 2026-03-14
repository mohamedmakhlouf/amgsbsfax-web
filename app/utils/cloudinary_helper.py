# app/utils/cloudinary_helper.py

def upload_file(file_obj, folder='amgsbsfax', resource_type='auto'):
    """Upload un fichier vers Cloudinary."""
    try:
        import cloudinary.uploader
        result = cloudinary.uploader.upload(
            file_obj,
            folder=folder,
            resource_type=resource_type,
        )
        return result
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        return {'secure_url': '', 'public_id': ''}

def delete_file(public_id, resource_type='image'):
    """Supprime un fichier de Cloudinary."""
    try:
        import cloudinary.uploader
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    except Exception as e:
        print(f"Cloudinary delete error: {e}")
