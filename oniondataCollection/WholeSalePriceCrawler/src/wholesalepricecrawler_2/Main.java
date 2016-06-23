package wholesalepricecrawler_2;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.browserlaunchers.locators.GoogleChromeLocator;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;

public class Main {

    
    static File logFile;
    static DateFormat dateFormat ;
    static Date date ;
    
    public static void main(String[] args) throws IOException {
        logFile =new File("logFile.txt");
        dateFormat = new SimpleDateFormat("dd/MM/yyyy HH:mm:SS");
        date = new Date();
        //if file doesnt exists, then create it
           if (!logFile.exists()) {
               logFile.createNewFile();
           }


        File lockFile;
        lockFile =new File("StateLockFile.txt");
    if(lockFile.exists())
    {
        SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MMMM-dd");
         Date RefDate =null;
         String tempDate="";
         int Refmandi=-1;
            try 
            {
                BufferedReader br = new BufferedReader(new FileReader(lockFile));
                tempDate=br.readLine().trim();
                if(tempDate!=null)
                    RefDate= formatter.parse(tempDate);
                else
                {
                    System.err.println("Error in initialising Reference Date");
                    System.exit(0);
                }
                if(br!=null)
                {
                String refMandiStr=br.readLine();
                if(refMandiStr!=null)
                    Refmandi=Integer.parseInt(refMandiStr);
                else
                {
                    System.err.println("Error in initialising Reference Mandi :: Error in Parsing Refernce mandi Code");
                    System.exit(0);
                }
                }
                else
                {
                    System.err.println("Error in initialising Reference Mandi");
                    System.exit(0);
                }
                lockFile.delete();
                System.out.println("Date Value "+RefDate);
                System.out.println("Mandi Code Value "+Refmandi);
            }
            catch(Exception e)
            {
                writeToLogFile(dateFormat.format(date)+"Error in parsing Date "+e.getMessage()+e.getStackTrace(), "Error");
            }
  
            
        String dateOfData =tempDate;
        int l=Refmandi;
            try{
        String url = "http://agmarknet.nic.in/agnew/NationalBEnglish/MarketWiseDailyReport.aspx?ss=2";

        //Parameters of the form :: as per observation name and ids are kept same
        String form_name = "form1";
        String yearDropdownID = "drpDwnYear";
        String monthDropdownID = "drpDwnMonth";
        String calenderID = "Calendar1";
        String selectStateID = "ListBox1";
        String submitButton = "Submit_list";
        //String mandiCheckBox = "GridView1_ctl03_RowLevelCheckBox";

        // Fetch the page
        WebDriver driver = new FirefoxDriver();
        driver.get(url);

        // Get Dropdon lists
        Select yearSelect = new Select(driver.findElement(By.id(yearDropdownID)));

        // Related parameters
        List<WebElement> yearOptions = yearSelect.getOptions();

        String tyear = "";
        String month = "";
        
        SimpleDateFormat df = new SimpleDateFormat("yyyy");
        int refyear =Integer.parseInt(df.format(RefDate));
        
        SimpleDateFormat dm = new SimpleDateFormat("MM");
        int refmonth = Integer.parseInt(dm.format(RefDate));
        
        System.out.println("refYear "+refyear);
        System.out.println("refMonth "+refmonth);
        //Select Year
        for (int i = refyear-2000; i <yearOptions.size(); i++) {

            dateOfData = "";

            yearSelect = new Select(driver.findElement(By.id(yearDropdownID)));
            yearOptions = yearSelect.getOptions();

            yearOptions.get(i).click();


            Select monthSelect = new Select(driver.findElement(By.id(monthDropdownID)));
            List<WebElement> monthOptions = monthSelect.getOptions();
            //Select Month
            for (int j = refmonth-1; j < monthOptions.size(); j++) {
  
                monthSelect.getOptions().get(j).click();
                monthSelect = new Select(driver.findElement(By.id(monthDropdownID)));
                monthOptions = monthSelect.getOptions();
                // get the table for selecting date
                WebElement formElement = driver.findElement(By.id(form_name));

                // get table from this form
                WebElement tableElement = formElement.findElement(By.id(calenderID));

                // get all the elements of the table
                List<WebElement> allCells = tableElement.findElements(By.tagName("td"));

                // check whether they have hyper link attached with them
                for (int k = 0; k < allCells.size(); k++) {

                    WebElement cell = allCells.get(k);
                    //cell.click();

                    //System.out.println("Cell :: " + cell.getText());
                    if (k == 0) {
                        String cellVal = cell.getText();
                        String[] monYear = cellVal.split(" ");
                        tyear = monYear[1];
                        month = monYear[0];
                    }

                    //if (cell.findElements(By.tagName("a")).size() > 0) {
                    if (cell.findElements(By.tagName("a")).size() > 0) {
                        
                        dateOfData = tyear + "-" + month + "-" + cell.getText();
                        Date date=null;
                         try {
                                  date = (Date) formatter.parse(dateOfData.trim());
                             } catch (Exception e) {
                                System.err.println("Error in convertion of dateofData " + dateOfData);
                                writeToLogFile("Error in convertion of dateofData " + dateOfData, "Error");
                                System.exit(0);
                            }
                         if(date.compareTo(RefDate)>=0)
                         {
                        WebElement hyperlink = cell.findElement(By.tagName("a"));

                        hyperlink.click();

                        // System.out.println("----- HYPERLINK CLICKED ------");

                        WebDriverWait wait = new WebDriverWait(driver, 3000);

                        wait.until(ExpectedConditions.presenceOfAllElementsLocatedBy(By.id(selectStateID)));
                        // Select State
                        Select stateSelect = new Select(driver.findElement(By.id(selectStateID)));
                        List<WebElement> allStates = stateSelect.getOptions();

                        for (l = Refmandi; l < allStates.size(); l++) {
                        WebElement state = allStates.get(l);
                            // System.out.println("State selected:" + state.getText());
                            state.click();
                        // get submit Button and click on them
                        WebElement submitElement = driver.findElement(By.id(submitButton));
                        submitElement.click();
                        // for all notchecked checkboxes
                        List<WebElement> mandis = driver.findElements(By.cssSelector(
                                "input:not(:checked)[type='checkbox']"));

                        //WebElement mandi = mandis.get(m);

                        for (int chkCount = 0; chkCount < mandis.size(); chkCount++) {
                            mandis.get(chkCount).click();
                            // System.out.println("Mandi Selected:" + mandis.get(chkCount).getAttribute("value"));
                        }
                            String submitMandi = "btnSubmit";
                            WebElement submitMandiButton = driver.findElement(By.id(submitMandi));
                            submitMandiButton.click();

                            try {
                               //System.out.println(date);
                                parsePage(driver, date);
                            } catch (Exception e) {
                                System.err.println("Error in parsing data " + dateOfData);
                                throw e;
                            }
                            driver.navigate().back();
                            wait = new WebDriverWait(driver, 1000);

                        driver.navigate().back();

                        wait = new WebDriverWait(driver, 3000);

                        wait.until(ExpectedConditions.presenceOfAllElementsLocatedBy(By.id(selectStateID)));

                         stateSelect = new Select(driver.findElement(By.id(selectStateID)));
                        stateSelect.deselectAll();
                        allStates = stateSelect.getOptions();
                        }
                       Refmandi=0;
                        System.gc();                       
                    }
                    }
                    // Reload the all elements of page
                    yearSelect = new Select(driver.findElement(By.id(yearDropdownID)));
                    yearOptions = yearSelect.getOptions();

                    monthSelect = new Select(driver.findElement(By.id(monthDropdownID)));
                    monthOptions = monthSelect.getOptions();

                    // Reload the Table
                    formElement = driver.findElement(By.id(form_name));

                    // get table from this form
                    tableElement = formElement.findElement(By.id(calenderID));

                    // get all the elements of the table
                    allCells = tableElement.findElements(By.tagName("td"));
                    System.gc();
                }


            }
            refmonth=1;
       
        }
        }catch(Exception fe)
        {
           
                System.err.println("Check");
                File stateLogFile = new File("StateLockFile.txt");
                if(stateLogFile.exists())
                    stateLogFile.delete();
                
                stateLogFile.createNewFile();

                FileWriter fileWritter1 = new FileWriter(stateLogFile.getName(), true);
                BufferedWriter bufferWritter1 = new BufferedWriter(fileWritter1);

                bufferWritter1.write(dateOfData+"\n");
                bufferWritter1.write(l+"\n");
                bufferWritter1.close();
          
                System.err.println("Error in parsing ");
                FileWriter fileWritter = new FileWriter(logFile.getName(), true);
                BufferedWriter bufferWritter = new BufferedWriter(fileWritter);

                DateFormat dateFormat = new SimpleDateFormat("dd/MM/yyyy HH:mm:SS");
                    //get current date time with Date()
                Date date = new Date();
                bufferWritter.write(dateFormat.format(date)+"Execution Stopped "+fe.getMessage()+fe.getStackTrace()+"\n");
                bufferWritter.close();
                System.exit(0);
           
        }
    }
    else
    {
        writeToLogFile(dateFormat.format(date)+"Process aborting Since Another Process is already running", "Error");      
    }
    
    }
    
    public static void writeToLogFile(String Message,String Type)
    {
          try{
       
                    FileWriter fileWritter = new FileWriter(logFile.getName(), true);
                    BufferedWriter bufferWritter = new BufferedWriter(fileWritter);

                    DateFormat dateFormat = new SimpleDateFormat("dd/MM/yyyy HH:mm:SS");
                       
                    Date date = new Date();
                    bufferWritter.write(dateFormat.format(date)+" "+Type+":::"+ Message);
                    bufferWritter.close();
                }
                catch(Exception ex)
                {
                    System.err.println("Error in Probably creating file ");
                } 
    }

    private static void parsePage(WebDriver driver, Date dateOfData) throws IOException {

        int rowCount = 1;
        String state = "";
        String mandiName = "";
        String commodity;
        String arrivals;
        String unitOfArrival;
        // we dont want origin
        String variety;
        String grade;
        String minimumPrice;
        String maximumPrice;
        String modalPrice;
        String unitOfPrice;

        // get table
        WebElement table = driver.findElement(By.id("GridView1")); // This table has data

        // get all rows
        List<WebElement> rows = table.findElements(By.tagName("tr"));

        // parse each row
        // 1st row is table heading
        // 2nd row is State
        // from 3rd row mandi starts
        for (WebElement row : rows) {

            // Skip the first row consists all headings
            if (rowCount == 1) {
                rowCount++;
                continue;
            }
            /*  We can also write this
            if(row.findElements(By.tagName("th")).size()>0)
            continue;
             */



            if (row.findElements(By.tagName("td")).size() == 1) {
                WebElement cellData = row.findElement(By.tagName("td"));
                if (cellData.getAttribute("align").equals("center")) {
                    state = cellData.getText();
                    rowCount++;
                    continue;
                } else if (cellData.getAttribute("align").equals("left")) {
                    mandiName = cellData.getText();
                    rowCount++;
                    continue;
                }
            } /* Row 2 contains state */ /*  if (rowCount == 2 && row.getAttribute("align").equals("center"))
            {
            WebElement cellData = row.findElement(By.tagName("td"));
            state = cellData.getText();
            rowCount++;
            continue;
            }*/ /* Now Mandis Will start */ /*   if (row.findElements(By.tagName("td")).size() == 1)
            {
            // Contains Mandi
            WebElement mandiNameWE = row.findElement(By.tagName("td"));
            mandiName = mandiNameWE.getText();
            rowCount++;
            continue;
            }*/ /* from here mandi data will start
            mandi name we should have already
            so this will have data for above mandi
             */ else {
                // Contains Mandi
                List<WebElement> cells = row.findElements(By.tagName("td"));

                // Cell has format
                //Commodity(Market Center)-Arrivals-Unit of Arrivals-Origin-Variety-Grade-Minimum Price-Maximum Price-Modal Price-Unit of Price
                if(cells.get(0).getText()!="")
                    commodity = cells.get(0).getText();
                else
                    continue;
                arrivals = cells.get(1).getText();
                unitOfArrival = cells.get(2).getText();
                // origin not needed : skip 3
                variety = cells.get(4).getText();
                grade = cells.get(5).getText();
                minimumPrice = cells.get(6).getText();
                maximumPrice = cells.get(7).getText();
                modalPrice = cells.get(8).getText();
                unitOfPrice = cells.get(9).getText();


                // System.out.print("State:"+state + " Mandi:"+mandiName+" Commodity:"+commodity+" Arrival:"+arrivals+" unitOfArrival"+unitOfArrival+" variety"+variety+" grade"+grade+" minimumPrice"+minimumPrice+" maximumPrice"+maximumPrice+" modalPrice"+modalPrice+" unitOfPrice"+unitOfPrice);
                int statecode = -1;
                int mandicode = -1;
                int commodityCode = -1;
                int commodityQualityCode = -1;
                try {
                    statecode = getStateCode(state);
                    mandicode = getMandiCode(statecode, mandiName);
                    commodityCode = getCommodityCode(commodity);
                    commodityQualityCode = getCommQualityCode(commodityCode, variety, grade);
                    InsertIntoWholeSaleTable(commodityQualityCode, mandicode, dateOfData, arrivals.trim(), unitOfArrival.trim(), minimumPrice.trim(), maximumPrice.trim(), modalPrice.trim(), unitOfPrice.trim());
                    //InsertIntoWholeSaleTable(state,mandiName,commodity,arrivals,unitOfArrival,variety,grade,minimumPrice,maximumPrice,modalPrice,unitOfPrice);

                    try {
                        File file = new File("/home/reshma/Desktop/WholeSaleTableSuccesslogs.txt");

                        //if file doesnt exists, then create it
                        if (!file.exists()) {
                            file.createNewFile();
                        }

                        //true = append file
                        FileWriter fileWritter = new FileWriter(file.getName(), true);
                        BufferedWriter bufferWritter = new BufferedWriter(fileWritter);
                        bufferWritter.write("Insertion Success  " + state + " " + mandiName + " " + commodity + " " + commodityQualityCode + " " + mandicode + " " + dateOfData + " " + arrivals + " " + unitOfArrival + " " + minimumPrice + " " + maximumPrice + " " + modalPrice + " " + unitOfPrice + "\n");
                        bufferWritter.close();
                    } catch (Exception e) {
                        System.err.println("Problem in writing to Success log file " + e.getMessage() + e.getStackTrace());
                    }
                    System.out.println("Insertion Success  " + state + " " + mandiName + " " + variety + " " + grade + " " + commodity + " " + commodityQualityCode + " " + mandicode + " " + dateOfData + " " + arrivals + " " + unitOfArrival + " " + minimumPrice + " " + maximumPrice + " " + modalPrice + " " + unitOfPrice);
                } catch (Exception e) {
                    System.out.println("Insertion UnSuccess " + e.getMessage() + e.getStackTrace() + " " + state + " " + statecode + " " + mandiName + " " + variety + " " + grade + " " + commodity + " " + commodityQualityCode + " " + mandicode + " " + dateOfData + " " + arrivals + " " + unitOfArrival + " " + minimumPrice + " " + maximumPrice + " " + modalPrice + " " + unitOfPrice);
                    try {
                        File file = new File("/home/reshma/Desktop/WholeSaleTableUnSuccesslogs.txt");

                        //if file doesnt exists, then create it
                        if (!file.exists()) {
                            file.createNewFile();
                        }

                        //true = append file
                        FileWriter fileWritter = new FileWriter(file.getName(), true);
                        BufferedWriter bufferWritter = new BufferedWriter(fileWritter);
                        bufferWritter.write("Insertion UnSuccess " + e.getMessage() + e.getStackTrace() + "\n");
                        bufferWritter.close();
                    } catch (Exception ex) {
                        System.err.println("Problem in writing to UnSuccess log file " + e.getMessage() + e.getStackTrace());
                    }

                }
                rowCount++;

            }

        }

    }

    private static int getMandiCode(int state, String mandi) throws Exception {
        Connection c = null;
        Statement stmt = null;
        int mandiCode = 0;
        try {
            Class.forName("org.postgresql.Driver");
            c = DriverManager.getConnection("jdbc:postgresql://localhost:5432/onion",
                    "postgres", "password");

            c.setAutoCommit(true);
            stmt = c.createStatement();
            String mandiInsert = "Insert into MANDIS(StateCode,MandiName) Values(?,?)";

            String mandiSelect = "Select * from MANDIS WHERE StateCode=? AND MandiName ilike ?";
            PreparedStatement mandiSelectPS = c.prepareStatement(mandiSelect);
            mandiSelectPS.setInt(1, state);
            mandiSelectPS.setString(2, mandi);

            ResultSet rs = mandiSelectPS.executeQuery();

            if (!rs.next()) {
                PreparedStatement ps = c.prepareStatement(mandiInsert);
                ps.setInt(1, state);
                ps.setString(2, mandi);

                ps.executeUpdate();
                ps.close();

                PreparedStatement mandiSelPS = c.prepareStatement(mandiSelect);
                mandiSelPS.setInt(1, state);
                mandiSelPS.setString(2, mandi);

                ResultSet rs1 = mandiSelPS.executeQuery();
                if (rs1.next()) {
                    mandiCode = rs1.getInt("MandiCode");
                }
                mandiSelPS.close();
                rs1.close();
                //stateSelPS.close();
            } else {
                mandiCode = rs.getInt("MandiCode");
            }

            mandiSelectPS.close();
            rs.close();

        } catch (Exception e) {
            throw e;
        } finally {
            c.close();
        }
        // System.out.println("Mandi Code ---"+mandiCode);
        return mandiCode;
    }

    private static int getStateCode(String state) throws Exception {
        Connection c = null;
        Statement stmt = null;
        int stateCode = 0;
        try {
            Class.forName("org.postgresql.Driver");
            c = DriverManager.getConnection("jdbc:postgresql://localhost:5432/onion",
                    "postgres", "password");

            c.setAutoCommit(true);
            stmt = c.createStatement();
            String stateInsert = "Insert into STATES(State) Values(?)";

            String stateSelect = "Select * from STATES WHERE State ilike ?";

            PreparedStatement stateSelectPS = c.prepareStatement(stateSelect);
            stateSelectPS.setString(1, state);

            ResultSet rs = stateSelectPS.executeQuery();

            if (!rs.next()) {
                PreparedStatement ps = c.prepareStatement(stateInsert);
                ps.setString(1, state);

                ps.executeUpdate();
                ps.close();

                PreparedStatement stateSelPS = c.prepareStatement(stateSelect);
                stateSelPS.setString(1, state);

                ResultSet rs1 = stateSelPS.executeQuery();
                if (rs1.next()) {
                    stateCode = rs1.getInt("StateCode");
                }
                stateSelPS.close();
                rs1.close();
            } else {
                stateCode = rs.getInt("StateCode");
            }
            stateSelectPS.close();
            rs.close();

        } catch (Exception e) {
            throw e;
        } finally {
            c.close();
        }

        // System.out.println("State Code ----"+stateCode);
        return stateCode;
    }

    private static int getCommodityCode(String commodity) throws Exception {
        Connection c = null;
        Statement stmt = null;
        int commodityCode = 0;
        try {
            Class.forName("org.postgresql.Driver");
            c = DriverManager.getConnection("jdbc:postgresql://localhost:5432/onion",
                    "postgres", "password");

            c.setAutoCommit(true);
            stmt = c.createStatement();
            String commodityInsert = "Insert into COMMODITY(CommodityName) Values(?)";

            String commoditySelect = "Select * from COMMODITY WHERE CommodityName ilike ?";

            PreparedStatement commoditySelectPS = c.prepareStatement(commoditySelect);
            commoditySelectPS.setString(1, commodity);

            ResultSet rs = commoditySelectPS.executeQuery();

            if (!rs.next()) {
                PreparedStatement ps = c.prepareStatement(commodityInsert);
                ps.setString(1, commodity);

                ps.executeUpdate();
                ps.close();

                PreparedStatement commSelPS = c.prepareStatement(commoditySelect);
                commSelPS.setString(1, commodity);

                ResultSet rs1 = commSelPS.executeQuery();
                if (rs1.next()) {
                    commodityCode = rs1.getInt("CommodityCode");
                }
                commSelPS.close();
                rs1.close();
            } else {
                commodityCode = rs.getInt("CommodityCode");
            }
            commoditySelectPS.close();
            rs.close();

        } catch (Exception e) {
            throw e;
        } finally {
            c.close();
        }
        //System.out.println("Commodity Code --"+commodityCode);
        return commodityCode;
    }

    private static int getCommQualityCode(int CommodityCode, String Variety, String Grade) throws Exception {
        Connection c = null;
        Statement stmt = null;
        int CommQualityCode = 0;
        try {
            Class.forName("org.postgresql.Driver");
            c = DriverManager.getConnection("jdbc:postgresql://localhost:5432/onion",
                    "postgres", "password");

            c.setAutoCommit(true);
            stmt = c.createStatement();
            String commQualityInsert = "Insert into VARIETY(CommodityCode,Variety,Grade) Values(?,?,?)";

            String commQualitySelect = "Select * from VARIETY WHERE CommodityCode=? AND Variety ilike ? AND Grade ilike ?";
            PreparedStatement commQualitySelectPS = c.prepareStatement(commQualitySelect);
            commQualitySelectPS.setInt(1, CommodityCode);
            commQualitySelectPS.setString(2, Variety);
            commQualitySelectPS.setString(3, Grade);

            ResultSet rs = commQualitySelectPS.executeQuery();

            if (!rs.next()) {
                PreparedStatement ps = c.prepareStatement(commQualityInsert);
                ps.setInt(1, CommodityCode);
                ps.setString(2, Variety);
                ps.setString(3, Grade);

                ps.executeUpdate();
                ps.close();

                PreparedStatement commQualitySelPS = c.prepareStatement(commQualitySelect);
                commQualitySelPS.setInt(1, CommodityCode);
                commQualitySelPS.setString(2, Variety);
                commQualitySelPS.setString(3, Grade);

                ResultSet rs1 = commQualitySelPS.executeQuery();
                if (rs1.next()) {
                    CommQualityCode = rs1.getInt("CommQualityCode");
                }
                commQualitySelPS.close();
                rs1.close();
                //stateSelPS.close();
            } else {
                CommQualityCode = rs.getInt("CommQualityCode");
            }

            rs.close();
            commQualitySelectPS.close();


        } catch (Exception e) {
            throw e;
        } finally {
            c.close();
        }

        //System.out.println("Commodity Quality Code--"+CommQualityCode);
        return CommQualityCode;
    }

    private static void InsertIntoWholeSaleTable(int commQualityCode, int MandiCode, Date dateOfDate, String arrivals, String unitOfArrival, String minimumPrice, String maximumPrice, String modalPrice, String unitOfPrice) throws IOException, Exception {
        Connection c = null;
        Statement stmt = null;
        try {
            Class.forName("org.postgresql.Driver");
            c = DriverManager.getConnection("jdbc:postgresql://localhost:5432/onion",
                    "postgres", "password");

            c.setAutoCommit(true);
            stmt = c.createStatement();



            String prepQuery = "Insert into WholeSaleData Values(?,?,?,?,?,?,?,?,?)";

            PreparedStatement ps = c.prepareStatement(prepQuery);

            int commqualitycode = 0;
            try {
                commqualitycode = commQualityCode;
                ps.setInt(1, commqualitycode);
            } catch (Exception e) {
                ps.setNull(1, java.sql.Types.INTEGER);
            }

            int mandicode = 0;
            try {
                mandicode = MandiCode;
                ps.setInt(2, mandicode);
            } catch (Exception e) {
                ps.setNull(2, java.sql.Types.INTEGER);
            }

            ps.setDate(3, new java.sql.Date(dateOfDate.getTime()));

            ps.setString(5, unitOfArrival);
            ps.setString(9, unitOfPrice);

            double arrival = 0;
            try {
                arrival = Double.parseDouble(arrivals);
                ps.setDouble(4, arrival);
            } catch (Exception e) {
                ps.setNull(4, java.sql.Types.DOUBLE);
            }

            double minimumprice = 0;
            try {
                minimumprice = Double.parseDouble(minimumPrice);
                ps.setDouble(6, minimumprice);
            } catch (Exception e) {
                ps.setNull(6, java.sql.Types.DOUBLE);
            }

            // System.out.println("Maximum Price Reeceived --"+maximumPrice);
            double maximumprice = 0;
            try {
                maximumprice = Double.parseDouble(maximumPrice);
                ps.setDouble(7, maximumprice);
            } catch (Exception e) {
                ps.setNull(7, java.sql.Types.DOUBLE);
                System.err.println("Error in parsing " + e.getMessage() + e.getStackTrace());
            }

            double modalprice = 0;
            try {
                modalprice = Double.parseDouble(modalPrice);
                ps.setDouble(8, modalprice);
            } catch (Exception e) {
                ps.setNull(8, java.sql.Types.DOUBLE);
            }

            ps.executeUpdate();
            ps.close();
            stmt.close();
            c.close();
            //System.out.println("Data saved into database");
        } catch (Exception e) {
            throw e;

        }
    }

    private static void InsertIntoWholeSaleTable(String state, String mandiName, String commodity, String arrivals, String unitOfArrival, String variety, String grade, String minimumPrice, String maximumPrice, String modalPrice, String unitOfPrice) throws IOException {
        Connection c = null;
        Statement stmt = null;
        try {
            Class.forName("org.postgresql.Driver");
            c = DriverManager.getConnection("jdbc:postgresql://localhost:5432/onion",
                    "postgres", "password");

            c.setAutoCommit(true);
            stmt = c.createStatement();



            String prepQuery = "Insert into WholeSaleData Values(?,?,?,?,?,?,?,?,?,?,?)";

            PreparedStatement ps = c.prepareStatement(prepQuery);
            ps.setString(1, state);
            ps.setString(2, mandiName);
            ps.setString(3, commodity);

            ps.setString(5, unitOfArrival);
            ps.setString(6, variety);
            ps.setString(7, grade);



            ps.setString(11, unitOfPrice);

            double arrival = 0;
            try {
                arrival = Double.parseDouble(arrivals);
                ps.setDouble(4, arrival);
            } catch (Exception e) {
                ps.setNull(4, java.sql.Types.DOUBLE);
            }

            double minimumprice = 0;
            try {
                minimumprice = Double.parseDouble(minimumPrice);
                ps.setDouble(8, minimumprice);
            } catch (Exception e) {
                ps.setNull(8, java.sql.Types.DOUBLE);
            }

            double maximumprice = 0;
            try {
                maximumprice = Double.parseDouble(maximumPrice);
                ps.setDouble(9, maximumprice);
            } catch (Exception e) {
                ps.setNull(9, java.sql.Types.DOUBLE);
            }

            double modalprice = 0;
            try {
                modalprice = Double.parseDouble(modalPrice);
                ps.setDouble(10, modalprice);
            } catch (Exception e) {
                ps.setNull(10, java.sql.Types.DOUBLE);
            }

            ps.executeUpdate();
            ps.close();
            stmt.close();
            c.close();
            //System.out.println("Data saved into database");
        } catch (Exception e) {
            File file = new File("/home/reshma/Desktop/WholeSaleAgriCultureErrorLogs.txt");

            //if file doesnt exists, then create it
            if (!file.exists()) {
                file.createNewFile();
            }

            //true = append file
            FileWriter fileWritter = new FileWriter(file.getName(), true);
            BufferedWriter bufferWritter = new BufferedWriter(fileWritter);
            bufferWritter.write(e.getMessage() + "\t" + e.getStackTrace() + "\n");
            bufferWritter.close();
        }
    }
}

