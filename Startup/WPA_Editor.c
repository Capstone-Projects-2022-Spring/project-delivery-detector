#include <unistd.h>
#include <string.h>
#include <stdio.h>
int main() {

    char network[100];
    char password[100];
    FILE* ptr;
    char ch;
    puts("What is the name of your network? (be mindful of caps, hit enter when finsihed)\n");
    fgets(network, 100, stdin);
    puts("What is the password? (hit enter when finished)\n");
    fgets(password, 100, stdin);
    if ((strlen(network) > 0) && (network[strlen (network) - 1] == '\n')){
        network[strlen (network) - 1] = '\0';
    }
    if ((strlen(password) > 0) && (password[strlen (password) - 1] == '\n')){
        password[strlen (password) - 1] = '\0';
    }
  
   printf("network: %s\npassword: %s\n", &network, &password);
   
    chdir("/volumes/boot");
    ptr = fopen("wpa_supplicant.conf", "w");
    if (NULL == ptr) {
        printf("file can't be opened \n");
	perror("error: ");
    }
    fprintf(ptr,"ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=US\nnetwork={\n\tssid=\"%s\"\n\tkey_mgmt=WPA-PSK\n\tpsk=\"%s\"\n}",&network,&password); 
    printf("Good to go!\n");
 
    // Closing the file
    fclose(ptr);
    return 0;
}
