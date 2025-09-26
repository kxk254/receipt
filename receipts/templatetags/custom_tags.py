from django import template

register = template.Library()

@register.filter
def get_image_url(object_list, selected_pdf_id):
    try:
        # Debug statements to see values
        print("object list:", object_list)
        print("selected pdf id:", selected_pdf_id)
        obj = object_list.get(id=selected_pdf_id)
        return obj.upload.url  # Adjust if necessary to return the correct URL
    except object_list.model.DoesNotExist:
        return ''  # Return an empty string if not found
    except Exception as e:
        print("Error fetching image URL:", e)
        return ''  # Handle any other unexpected errors