import zipimport
module = zipimport.zipimporter('./scripts/webapi.zip').load_module('webapi')

get_class = module.get_class
