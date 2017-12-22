package gluu.scim2.client;
import gluu.scim2.client.factory.ScimClientFactory;
import org.gluu.oxtrust.model.scim2.*;
import org.jboss.resteasy.client.core.BaseClientResponse;

import javax.ws.rs.core.MediaType;
import javax.xml.bind.JAXBException;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Properties;

public class TestScimClient {
	// For details: https://gluu.org/docs/ce/user-management/scim2/#testing-with-the-scim-client-uma
	// Insert hostname here
    private String domain = "https://<host-name>/identity/restv1";
	// Insert umaAatClientId here
    private String umaAatClientId = "";
    private String umaAatClientJksPath = "/path/to/scim-rp.jks";
	// JksPassword defaults to secret
    private String umaAatClientJksPassword = "secret";
    private String umaAatClientKeyId = "";
    ScimClient client = ScimClientFactory.getClient(domain, null, umaAatClientId, umaAatClientJksPath, umaAatClientJksPassword, umaAatClientKeyId);
	
	
	// Basic add user functionality for testing. You can make this more robust for inputs.
	
    public void addUser() {
        User user = new User();

        Name name = new Name();
        name.setGivenName("Test");
        name.setFamilyName("Test");
        user.setName(name);

        user.setActive(true);

        user.setUserName("newUser_" + new Date().getTime());
        user.setPassword("secret");
        user.setPreferredLanguage("US_en");
        user.setDisplayName("John");

        List<Email> emails = new ArrayList<Email>();
        Email email = new Email();
        email.setPrimary(true);
        email.setValue(new Date().getTime() + "@test.com");
        email.setDisplay(new Date().getTime() + "@test.com");
        email.setType(Email.Type.WORK);
        email.setReference("");
        emails.add(email);
        user.setEmails(emails);

        List<PhoneNumber> phoneNumbers = new ArrayList<PhoneNumber>();
        PhoneNumber phoneNumber = new PhoneNumber();
        phoneNumber.setPrimary(true);
        phoneNumber.setValue("123-456-7890");
        phoneNumber.setDisplay("123-456-7890");
        phoneNumber.setType(PhoneNumber.Type.WORK);
        phoneNumber.setReference("");
        phoneNumbers.add(phoneNumber);
        user.setPhoneNumbers(phoneNumbers);

        List<Address> addresses = new ArrayList<Address>();
        Address address = new Address();
        address.setPrimary(true);
        address.setValue("test");
        address.setDisplay("My Address");
        address.setType(Address.Type.WORK);
        address.setReference("");
        address.setStreetAddress("My Street");
        address.setLocality("My Locality");
        address.setPostalCode("12345");
        address.setRegion("My Region");
        address.setCountry("RU");
        address.setFormatted("My Formatted Address");
        addresses.add(address);
        user.setAddresses(addresses);

        try {
            BaseClientResponse<User> response = client.createUser(user, new String[]{});
            System.out.println("response HTTP code = {}" + response.getStatus());
			
			// Check if the HTTP response is proper.
			
            if (String.valueOf(response.getStatus()).equals("201")) {
                System.out.println("User " + user.getUserName() + " added.");
                System.out.println("Add successful.\n");
            }else {
                System.out.println("Something went wrong.\n");
            }
        } catch (IOException e) {
            System.out.println("Failed to add user.");
            e.printStackTrace();
        }
    }


    public void simpleSearch() throws Exception {

        String filter = "givenName eq \"Test\"";

        BaseClientResponse<ListResponse> response = client.searchUsers(filter, 1, 1, "", "", null);
        List<Resource> results=response.getEntity().getResources();

        System.out.println("Length of results list is: " + results.size());
        User user=(User) results.get(0);
        System.out.println("First user in the list is: " + user.getUserName());

    }
	
	// Search all. Maxes out at 200 results in 3.1.1
	
    public void simpleSearchAll() throws Exception {

        BaseClientResponse<ListResponse> response = client.retrieveAllUsers();
        List<Resource> results=response.getEntity().getResources();

        System.out.println("Length of results list is: " + results.size());
        for (int i = 0; i < results.size(); i ++) {
            User user=(User) results.get(i);

            // Remove Admin from search results
            if (user.getDisplayName().equals("Default Admin User")){
                continue;
            } else {
                System.out.println("First user in the list is: " + user.getDisplayName());
                System.out.println("First inum in the list is: " + results.get(i).getId());
                String test = results.get(i).getId();
            }
        }
    }
	
    public void delUser() {
		// Must enter entry inum here
        String id = "@!EF26.C4E5.43A0.DC8A!0001!FF43.BC12!0000!7216.1548.D99B.CD5D";
        try {

            //System.out.println(client.deletePerson(id).getStatus());
            int DeleteStatus = client.deletePerson(id).getStatus();
            if (String.valueOf(DeleteStatus).equals("404")) {
                System.out.println("Deletion failure with 404.");
            } else {
                System.out.println("Successfully deleted inum: " + id);
            }
        } catch (IOException e) {
            e.printStackTrace();
            System.out.println("Failed to delete user.");
        }
    }

    // Only deletes up to 200 @ a time. I think the API response is limited

    public void delAll() throws Exception {

        List ids = new ArrayList();

        BaseClientResponse<ListResponse> response = client.retrieveAllUsers();
        List<Resource> results=response.getEntity().getResources();

        System.out.println("Length of results list is: " + results.size());

        //Get all users and add to list

        for (int i = 0; i < results.size(); i ++) {
            User user = (User) results.get(i);

            // Remove Admin from search results
            if (user.getDisplayName().equals("Default Admin User")) {
                continue;
            } else {
                String test = results.get(i).getId();
                //System.out.println(test.toString());
                ids.add(test);
            }
        }
        // Take inums from ids list and delete users that aren't admin
        for (int i = 0; i < ids.size(); i++) {
            try {
                User user = (User) results.get(i);
                //if (user.getDisplayName().equals("Default Admin User")) {
                    //continue;
                //} else {
                    BaseClientResponse<User> del = client.deletePerson(String.valueOf(ids.get(i)));
                    System.out.println("Deleting:");
                    System.out.println("User " + user.getUserName() + "\nWith inum: " + ids.get(i));
                    System.out.println("response HTTP code = {}" + del.getStatus());
                    int status = del.getStatus();
                    if (String.valueOf(status).equals("204")){
                        System.out.println("Deletion successful\n");
                    } else {
                        System.out.println("Could not delete " + user.getUserName() + ". Something went wrong.");
                    }

                //}
            } catch (IOException e) {
                e.printStackTrace();
            }
            //System.out.println("User deleted.");
        }
    }

    public void multiAdd() {

        // Add n amount of users with 'numUsers'

        for (int numUsers = 1000; numUsers>0;numUsers--){
            TestScimClient scim = new TestScimClient();
            scim.addUser();
        }
    }



    public static void main(String[] args) throws Exception {

        TestScimClient scim = new TestScimClient();
        //scim.simpleSearch();
        //scim.simpleSearchAll();
	
        //scim.delUser();
  	// Snippet of code to iterate through all 200 entries returned from 'retrieveAllUsers()'
        /*
        int n = 0;
        for (int i = 10; n<=i;n++) {
            scim.delAll();
            System.out.println("\n\n\n\nIteration: " + n + "\n\n\n\n");
        }
        */
        //scim.loadJson();
        //scim.addUser();
        //scim.multiAdd();
    }
}
