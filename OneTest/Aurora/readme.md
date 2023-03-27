# OneTest Performance - Sample Script for Aurora Store

A key aspect of performance testing is the ability to simulate concurrent user load. The - OneTest Performance sample script for Emerald store - provides you with a sample project to generate and simulate user traffic against the Emerald store.
The script includes common search, browse, and checkout scenarios. The functionalities are not all inclusive and needs to be adapted to match your store customization and usage patterns.
The following steps will guide on how to import the script, set it up and start using it 

## Setting up the script  
The package comes in a zip file that contains the OneTest Performance script file  

The script was written with HCL Onetest Performance Version 10.2  
![image](https://github01.hclpnp.com/storage/user/1546/files/c68ccacf-66ee-4518-a3d3-9b98590b82aa)



You would need 3 steps to setup the OneTest performance script. 
- A. Import the script  
- B. Import the libraries  
- C. Clean the project  

The details on these steps one by one will be found below:  

**A. Import the package**
1. Download the package file (zip file) to your machine and save it under a new folder 
2. Open OneTest and choose a new workspace, choose a location and an appropriate workspace name  
   ![image](https://github01.hclpnp.com/storage/user/1546/files/d777f94e-1d90-49b6-a266-00a50424532b)    
3. Close the Welcome tab  
4. Right click in the Test Navigator and select Import  
   ![image](https://github01.hclpnp.com/storage/user/1546/files/c0c1bd31-fa23-4590-bce8-68dcbda8dd84)  
5. Select Test > Test Asset with Dependencies and click Next. Select the file you downloaded in step 1 and then click Finish.  
   ![image](https://github01.hclpnp.com/storage/user/1546/files/8708e341-2d8e-4124-b6a9-10b8fbdc1933)

**B. Clean the project**  
1. Click on menu Project and choose Clean command  
2. On the Clean window, ensure the project is select and click on Clean button  
![image](https://github01.hclpnp.com/storage/user/1546/files/5bcf20f6-8284-4df7-9465-841785fd6015)  

## Updating the script before using it  
Once the script has been imported and setup, you would need to make updates and apply initializations before you can start using it. For this, you would also need 3 steps as before:  
- A. Update global variables.  
- B. Update Datapools.  
- C. Update Schedules.  

The details for each step are below:  

**A – Update global variables**  
All the global variables reside inside the module *Init* as shown in the following screenshot  
Select Resource View (highlighted icon in the screenshot), expand Modules, open init module and expand Test Resources and Test Variables to see all the global variables.  
Change the values of the variables corresponding to your environment.  

![image](https://github01.hclpnp.com/storage/user/1546/files/03a09bd1-8513-4a23-a8e8-568e9d15b3d2)  

The variables that need to be updated before using the performance script are:

| Variable | Description |
| --- | --- | 
| hostname | The hostname used in the URL of the e-commerce storefront | 
| store_name | The store name.<br>The complete URL of the storefront is hostname:port_num/store_name | 
| store_id | The store id.<br>The default store ids are 11 for Emerald B2C store and 12 for B2B Sapphire store.<br>The store Administrator can provide store ids | 
| catalog_id | The catalogue id used in the store.<br>The store Administrator can provide catalogue ids | 
| lang_id	| The default language id of the store.<br>-1 is English | 
| min_items_in_cart | Minimum number of items in the cart |
| max_items_in_cart | Maximum number of items in the cart. To set a fixed number to be always added to the cart, set min and max to that number |
| fixed_number_of_items_in_cart | This variable shows if the number of items in the cart is fixed throughout the run or is randomly calculated for each user. The value of this variable can be "fixed" or "random" | 
| users_password | The password used for registered users. The script is configured to use a single password for all registered users.<br>If you plan to use a different password for each user, you may need to create a different Datapool with 2 columns, one for the userId and one for its password | 
| email_domain | The email domain that will be added automatically to the users' emails. It is set by default to ‘company.com’, so the emails will be with this format lastname@company.com | 
| enable_80_20 | This variable enables (when equal to 1) or disables (when equal to 0) the 80/20 rule.<br>When 80/20 rule is enabled by setting this variable to 1, it’ll change the way to pick randomly the categories and the products. 20% of categories and 20% of products will be picked 80% of the time. This will increase cache hit.<br>When the 80/20 rule is disabled by setting this variable to 0, all the items in the storefront are picked randomly without any rule | 


**B – Update Datapools**  
   1. In the Test Navigator, open Datapools folder.
   2. Datapool *random_words* has terms related to out-of-the-box catalog. Open it by right clicking on it > Open with > Text Editor.  
      You can change the content to put search terms related to your catalogue.
   3. Datapool *users* contains registered users. You can open it and update it with other userids that you previously prepared and loaded to the database. Users with the format *hclu%* are pre-added in the datapool. <br>The registered users need to be loaded to your database ahead of starting the performance test. The users' passwords need also to be set for these new registered users as set by the variable users_password shown above.<br>    
This page gives an example on how to load registered users:  
[Sample: Loading registered users](https://help.hcltechsw.com/commerce/9.1.0/data/refs/rmlsamplepeople.html)  
And this page gives a general overview or the dataload utility:  
[Overview of the Data Load utility](https://help.hcltechsw.com/commerce/9.1.0/data/concepts/cmlbatchoverview.html)

You can also use a schedule to add registered users to the database. It's explained in the next section. 

**C – Update Schedules**
  1. There are 3 schedules in this project:
  
| Schedule | Description | 
| --- | --- |
| OneTest_B2C_Aurora | This schedule is the most important schedule. This is the one to use to generate load on your Commerce. |
| Test_OneTest_B2C_Aurora | same as OneTest_B2C_Aurora. It should be used for testing and debugging new modules or custom codes. It uses less users and the trace log is enabled (set to All). You may disable/enable portions of the schedules to test a part of the shopping flow |
| AddNewUsers | This schedule can be used to add registered users. The only disadvantage with using this schedule vs loading the users with *dataload* is that the schedule is very slow to add a high number of users while it takes few minutes with *dataload*. |

  2. It is important that you check and update the following as required before running a performance test:  
  
**a. Show Advanced**  
When you open the schedule the first time, check Show Advanced checkbox to show up the “Change Rate” and “Settle Time” columns  

![image](https://github01.hclpnp.com/storage/user/1546/files/692a981d-3055-4061-8741-596ae7e270dc)   

**b. User stage characteristics**  
To change user stage, select the row in the screenshot above and click on Edit. In the popup, you can change the number of users, duration of the run, the rate of starting the users and the settle time.  

![image](https://github01.hclpnp.com/storage/user/1546/files/b42628ff-e21d-4b2e-9079-c6a6aac325a7)  

The above setting runs the schedule using 60 users for 1h. The 60 users are set to start over 2 mins.
The preview will change based on the above updates as follow:

![image](https://github01.hclpnp.com/storage/user/1546/files/4f45f8f2-307a-4605-8e99-38f9a4bd1625)    

**c. Think time**  
To check think time, click the drop down category and select Think Time. 
The think time is the time that OneTest insert between one request and the next one. It is small for stress load and between 2 to 5s for reliability load.  

![image](https://github01.hclpnp.com/storage/user/1546/files/6df8a555-03fa-4a03-aac0-cc6c8cee167e)

**d. Statistics sampling**  
Check the statistics sampling by setting the log level and the interval time used by OneTest to gather statistics.  

![image](https://github01.hclpnp.com/storage/user/1546/files/7ea168ed-d2c3-4334-be45-6f6ce3e465e3)

Increase the interval for long runs and decrease it for small runs.  

**e. Test log** 
If you’re debugging an issue, you can set a small number of users and set log levels to All. For long production runs and especially for high number of users, you should un-check Show errors and failures, warning and other types  

![image](https://github01.hclpnp.com/storage/user/1546/files/71a5171b-835b-42b1-89c1-29a283877d17)  

**f. Transactions Weight**  
Open the schedule and select Random Selector. In the right pane, you can change the weight based on the scenario you want to run. Changing the weight will change the percentage of the block on the schedule.  

![image](https://github01.hclpnp.com/storage/user/1546/files/65a8609b-7906-4e42-8382-4c7643c1ed2d)  

## Run the schedule  

Once the previous steps are applied, open TestB2CFlow schedule and run it with 1 user for few minutes with full logs to check out for any issues    

![image](https://github01.hclpnp.com/storage/user/1546/files/54a134ae-374e-4262-85b7-1ebbbcfae900)  



