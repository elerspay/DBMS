#include <string.h>
#include "database/dbms.h"

extern "C" char run_parser(const char *input);

int main(int argc, char *argv[])
{
    // Check for auth args
    const char* user = nullptr;
    const char* pass = nullptr;
    
    for(int i=1; i<argc; i++) {
        if(strcmp(argv[i], "-u") == 0 && i+1 < argc) user = argv[++i];
        if(strcmp(argv[i], "-p") == 0 && i+1 < argc) pass = argv[++i];
    }
    
    if (user && pass) {
        dbms::get_instance()->login(user, pass);
    }

	if(argc < 2 || (user && argc < 6))
	{
		return run_parser(nullptr);
	} else {
		return 0;
	}
	return 0;
}
