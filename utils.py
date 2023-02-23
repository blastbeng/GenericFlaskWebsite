import os

def guess_mymetype(data: str):
  filename, file_extension = os.path.splitext(data)
  if file_extension == '.jpg' or file_extension == '.jpeg':
    return 'image/jpeg'
  elif file_extension == '.png':
    return 'image/png'
  elif file_extension == '.gif':
    return 'image/gif'
  else:
    return 'image/unknown-type'