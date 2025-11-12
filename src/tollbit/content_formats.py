from tollbit._apis.models import Format as APIFormat

# We create an alias here in order to allow us to change the underlying
# implementation without affecting users of this module.
Format = APIFormat

html = APIFormat.html
markdown = APIFormat.markdown
