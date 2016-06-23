/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package retailpricecrawer_1;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.StringWriter;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.InetSocketAddress;
import java.net.MalformedURLException;
import java.net.Proxy;
import java.net.URL;
import java.net.URLEncoder;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;
import sun.nio.cs.StandardCharsets;

/**
 *
 * @author reshma
 */
public
        class Main
{

    /**
     * @param args the command line arguments
     */
    static
            File logFile;

    public static
            void main(String[] args) throws ParseException, ParserConfigurationException, UnsupportedEncodingException, IOException, SAXException, Exception
    {
        int noOfYears = 15;
        int latestMonth = 3;
        int latestDate = 15;
        int latestYear = 2015;

        logFile = new File("logFile.txt");
        //if file doesnt exists, then create it
        if (!logFile.exists())
        {
            logFile.createNewFile();
        }

        File lockFile;
        lockFile = new File("StateLockFile.txt");

        if (lockFile.exists())
        {
            SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MMMM-dd");
            Date RefDate = null;
            String tempDate = "";

            try
            {
                BufferedReader br = new BufferedReader(new FileReader(lockFile));
                tempDate = br.readLine();
                if (tempDate != null)
                {
                    RefDate = formatter.parse(tempDate.trim());
                }
                else
                {
                    System.err.println("Error in initialising Reference Date");
                    System.exit(0);
                }

                lockFile.delete();
                System.out.println("Date Value " + RefDate);

            }
            catch (Exception e)
            {
                try
                {

                    FileWriter fileWritter = new FileWriter(logFile.getName(), true);
                    BufferedWriter bufferWritter = new BufferedWriter(fileWritter);

                    DateFormat dateFormat = new SimpleDateFormat("dd/MM/yyyy HH:mm:SS");
                    //get current date time with Date()
                    Date date = new Date();
                    bufferWritter.write(dateFormat.format(date) + "Error in parsing Date " + e.getMessage() + e.getStackTrace());
                    bufferWritter.close();
                }
                catch (Exception ex)
                {
                    System.err.println("Error in Probably creating file ");
                }
            }
            
            WebDriver driver = new FirefoxDriver();

            DateFormat dateFormat = new SimpleDateFormat("dd/MM/yyyy");
            Calendar cal = Calendar.getInstance();
            cal.setTime(RefDate);

            String dateTofetch = dateFormat.format(cal.getTime());
            for (int i = 1; i < 5110; i++)
            {

                driver.get("http://fcainfoweb.nic.in/PMSver2/Reports/Report_Menu_web.aspx");

                WebElement option = driver.findElement(By.id("MainContent_Rbl_Rpt_type_0"));

                option.click();

                WebDriverWait wait = new WebDriverWait(driver, 3000);

                wait.until(ExpectedConditions.presenceOfAllElementsLocatedBy(By.id("MainContent_Ddl_Rpt_Option0")));

                Select locator = new Select(driver.findElement(By.id("MainContent_Ddl_Rpt_Option0")));

                locator.getOptions().get(1).click();

                wait = new WebDriverWait(driver, 3000);

                wait.until(ExpectedConditions.presenceOfAllElementsLocatedBy(By.id("MainContent_Txt_FrmDate")));

                WebElement textElement = driver.findElement(By.id("MainContent_Txt_FrmDate"));

                // Here We are sending Date ... We need to generate the all dates, but how?
                textElement.sendKeys(dateTofetch);

                driver.findElement(By.id("MainContent_btn_getdata1")).click();

                /**
                 * ****************************************************************
                 * PARSE DATA HERE *
                 * ****************************************************************
                 */
                if (!driver.findElement(By.tagName("body")).getText().contains("Sorry, Data does not exist for this date"))
                {
                    parseData(driver);
                }
                /**
                 * *****************************************************************
                 * PARSING DONE *
                 * ****************************************************************
                 */
                wait.until(ExpectedConditions.presenceOfAllElementsLocatedBy(By.id("btn_back")));

                driver.findElement(By.id("btn_back")).click();

                cal.add(Calendar.DAY_OF_YEAR, +1);
                dateTofetch = dateFormat.format(cal.getTime());

                System.out.println("Run Complete " + i);

            }
        }
        else
        {
            try
            {

                FileWriter fileWritter = new FileWriter(logFile.getName(), true);
                BufferedWriter bufferWritter = new BufferedWriter(fileWritter);

                DateFormat dateFormat = new SimpleDateFormat("dd/MM/yyyy HH:mm:SS");
                //get current date time with Date()
                Date date = new Date();
                bufferWritter.write(dateFormat.format(date) + "Process aborting Since Another Process is already running \n");
                bufferWritter.close();
            }
            catch (Exception e)
            {
                System.err.println("Error in Probably creating file ");
            }
        }
    }

    private static
            void parseData(WebDriver driver) throws ParseException, ParserConfigurationException, IOException, UnsupportedEncodingException, SAXException, Exception
    {
        // Get All The tables from the page
        List<WebElement> allTables = driver.findElements(By.tagName("table"));

        // We need to parse tables which all are required
        // Consider all tables one by one
        String date = "";
        String unitInKG = "";
        String unitInLt = "";

        for (int i = 0; i < allTables.size(); i++)
        {

            // For debug purpose
            System.out.println("Table :" + (i) + "\n\n" + allTables.get(i).getText());
            System.out.println("\n\n");

            if (i % 4 == 0)
            {
                // Table Type 1
                // Get Date and Unit of Price
                // Consists Only One Row
                // consists of 3 elements
                // Date - Daily Retail Prices Of Essential Commodities - Unit

                // Get the row
                WebElement row = allTables.get(i).findElement(By.tagName("tr"));

                // Get 3 Cells (Columns)
                List<WebElement> cells = row.findElements(By.tagName("td"));

                // 1st Element has of format : Date<space><space><Actual Date>
                String temp = cells.get(0).getText();
                String elements[] = temp.split("  ");
                date = elements[1];

                // 3rd element consists of price
                // and has format Unit:&nbsp;(Rs./Kg.)
                temp = cells.get(2).getText();
                elements = temp.split(" ");
                unitInKG = elements[1];
            }
            else if (i % 4 == 2)
            {
                // Table type 3
                // Parsing this before to get unit of Milk

                // Consists Of 3 rows
                // Only 1st is important
                // get rows
                List<WebElement> rows = allTables.get(i).findElements(By.tagName("tr"));

                // first row has 2 cells, out of which 2nd is required
                // get the cells of the first row
                List<WebElement> cells = rows.get(0).findElements(By.tagName("td"));

                // 2nd cells consists text as
                // <font size=2 color=Black><b>NR</b> -> Not Reported &nbsp;&nbsp;&nbsp;&nbsp; <b>@</b> -> (Rs./Lt.)</font> &nbsp;&nbsp;&nbsp;&nbsp; <b>*</b> -> (Packed)
                // What to do now ???
            }
            else if (i % 4 == 1)
            {
                // Table type 2
                // Actual data
                // Now this tables has some rows
                // 1st row is always with the list of commodities, in that also
                // 1st cell is always "center"

                // with the rest of the rows, if it has only one element, then it is stating zone
                // else if it has more than one element then first element is center i.e. place
                // and rest is the retail price
                // So lets do it
                // get all rows
                List<WebElement> rows = allTables.get(i).findElements(By.tagName("tr"));

                // process each row
                List<WebElement> commodities = null;
                for (int j = 0; j < rows.size(); j++)
                {
                    if (j == 0)
                    {
                        // its 1st row
                        // all commodities
                        // get all cells/columns/elements
                        commodities = rows.get(j).findElements(By.tagName("td"));
                        // So these cells has all the commodity list
                        // EXCEPT first cell, which has word "center"
                        continue;
                    }

                    // Other than first row
                    // get cells
                    List<WebElement> cells = rows.get(j).findElements(By.tagName("td"));

                    if (cells.size() >= 1)
                    {
                        String firstCellData = cells.get(0).getText();
                        if (firstCellData.equals("Maximum Price") || firstCellData.equals("Minimum Price") || firstCellData.equals("Modal Price"))
                        {
                            continue; // We can also write break over here
                        }
                    }
                    if (cells.size() == 1)
                    {
                        // Consists ZONE
                        // NOT Required
                    }
                    else
                    {
                        // Consists data
                        // 1st element is Center
                        // Rest Prices Of Commodities

                        // Process This
                        for (int k = 1; k < cells.size(); k++)
                        {
                            System.out.print("Date:" + date + " ");

                            SimpleDateFormat formatter = new SimpleDateFormat("dd/MM/yyyy");
                            Date dateOfData = (Date) formatter.parse(date.trim());
                            if (!commodities.isEmpty())
                            {
                                String commoTemp = commodities.get(k).getText().trim();
                                String unit = "";
                                if (commoTemp.contains("@"))
                                {
                                    commoTemp = commoTemp.replace("@", "");
                                    System.out.print("Comodity:" + commoTemp + " ");
                                    System.out.print("Unit: " + unitInLt + " ");
                                    unit = "unitInLt";
                                }
                                else
                                {
                                    if (commoTemp.contains("*"))
                                    {
                                        commoTemp = commoTemp.replace("*", "");
                                    }
                                    System.out.print("Comodity:" + commoTemp + " ");
                                    System.out.print("Unit: " + unitInKG + " ");
                                    unit = "unitInKG";
                                }

                                String centerName = cells.get(0).getText().trim();

                                try
                                {
                                    int centerCode;
                                    int centerFind = getCenterCode(centerName);

                                    if (centerFind == 0)
                                    {
                                        // Could not find center into the database
                                        String stateName = getStateName(centerName);
                                        System.out.println("STATE NAME FETCHED FROM GOOGLE API: "+stateName + "... ");
                                        int stateCode = getStateCode(stateName);
                                        System.out.println("GOT STATE CODE");
                                        String location[] = new String[2];

                                        location = fetchLocation(centerName, stateName);
                                        System.out.println("FETCHED LOCATION");
                                        centerCode = InsertIntoCenter(centerName, stateCode, location[0], location[1]);
                                        
                                    }
                                    else
                                    {
                                        centerCode = centerFind;
                                    }

                                    String price = cells.get(k).getText().trim();

                                    InsertIntoRetail(centerCode, price, dateOfData);
                                }
                                catch (Exception e)
                                {
                                    System.err.println("Exception related to database " + e.getMessage() + e.getStackTrace());
                                }
                            }
                            else
                            {
                                System.out.println("Error! Commodity List not initialised");
                            }

                            System.out.print("Center:" + cells.get(0).getText() + " ");
                            System.out.print("Price:" + cells.get(k).getText());
                            System.out.println("");
                        }

                    }
                }
            }
            else if (i % 4 == 3)
            {
                // Table type 4
                // We do not need to parse this table
            }
        }

    }

    private static
            String getStateName(String centerName) throws UnsupportedEncodingException, ParserConfigurationException, SAXException, IOException
    {

        int responseCode = 200;
        String api = "http://maps.googleapis.com/maps/api/geocode/xml?address=" + URLEncoder.encode(centerName, "UTF-8") + "&sensor=true";

        System.out.println("API " + api);
        URL url = new URL(api);
        HttpURLConnection httpConnection = (HttpURLConnection) url.openConnection();
        
        // Setting Proxy
        Proxy proxy = new Proxy(Proxy.Type.HTTP, new InetSocketAddress("10.10.78.62", 3128));
        httpConnection = (HttpURLConnection) url.openConnection(proxy);
        
        httpConnection.connect();
        responseCode = httpConnection.getResponseCode();
        if (responseCode == 200)
        {
            try
            {
                DocumentBuilder builder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
                //String strRes="<GeocodeResponse><status>OK</status><result><type>locality</type><type>political</type><formatted_address>Kanpur, Uttar Pradesh, India</formatted_address><address_component><long_name>Kanpur</long_name><short_name>Kanpur</short_name><type>locality</type><type>political</type></address_component><address_component><long_name>Kanpur Nagar</long_name><short_name>Kanpur Nagar</short_name><type>administrative_area_level_2</type><type>political</type></address_component><address_component><long_name>Uttar Pradesh</long_name><short_name>UP</short_name><type>administrative_area_level_1</type><type>political</type></address_component><address_component><long_name>India</long_name><short_name>IN</short_name><type>country</type><type>political</type></address_component><geometry><location><lat>26.4499230</lat><lng>80.3318736</lng></location><location_type>APPROXIMATE</location_type><viewport><southwest><lat>26.3512674</lat><lng>80.2087784</lng></southwest><northeast><lat>26.5430800</lat><lng>80.4679871</lng></northeast></viewport><bounds><southwest><lat>26.3512674</lat><lng>80.2087784</lng></southwest><northeast><lat>26.5430800</lat><lng>80.4679871</lng></northeast></bounds></geometry><place_id>ChIJb8QnsXBHnDkRQXu-nyoweBc</place_id></result><result><type>locality</type><type>political</type><formatted_address>Kanpur, Uttar Pradesh 209865, India</formatted_address><address_component><long_name>Kanpur</long_name><short_name>Kanpur</short_name><type>locality</type><type>political</type></address_component><address_component><long_name>Unnao</long_name><short_name>Unnao</short_name><type>administrative_area_level_2</type><type>political</type></address_component><address_component><long_name>Uttar Pradesh</long_name><short_name>UP</short_name><type>administrative_area_level_1</type><type>political</type></address_component><address_component><long_name>India</long_name><short_name>IN</short_name><type>country</type><type>political</type></address_component><address_component><long_name>209865</long_name><short_name>209865</short_name><type>postal_code</type></address_component><geometry><location><lat>26.3201324</lat><lng>80.5841155</lng></location><location_type>APPROXIMATE</location_type><viewport><southwest><lat>26.3125700</lat><lng>80.5787200</lng></southwest><northeast><lat>26.3243099</lat><lng>80.5892201</lng></northeast></viewport><bounds><southwest><lat>26.3125700</lat><lng>80.5787200</lng></southwest><northeast><lat>26.3243099</lat><lng>80.5892201</lng></northeast></bounds></geometry><place_id>ChIJsRP7YHRvnDkRg3c4ISL54Lo</place_id></result><result><type>locality</type><type>political</type><formatted_address>Kanpur, Madhya Pradesh 485331, India</formatted_address><address_component><long_name>Kanpur</long_name><short_name>Kanpur</short_name><type>locality</type><type>political</type></address_component><address_component><long_name>Satna</long_name><short_name>Satna</short_name><type>administrative_area_level_2</type><type>political</type></address_component><address_component><long_name>Madhya Pradesh</long_name><short_name>MP</short_name><type>administrative_area_level_1</type><type>political</type></address_component><address_component><long_name>India</long_name><short_name>IN</short_name><type>country</type><type>political</type></address_component><address_component><long_name>485331</long_name><short_name>485331</short_name><type>postal_code</type></address_component><geometry><location><lat>24.8739100</lat><lng>80.7824012</lng></location><location_type>APPROXIMATE</location_type><viewport><southwest><lat>24.8572700</lat><lng>80.7693900</lng></southwest><northeast><lat>24.8908600</lat><lng>80.7970400</lng></northeast></viewport><bounds><southwest><lat>24.8572700</lat><lng>80.7693900</lng></southwest><northeast><lat>24.8908600</lat><lng>80.7970400</lng></northeast></bounds></geometry><place_id>ChIJZwNDWEFigzkRm0FL4_-kOk0</place_id></result></GeocodeResponse>";
                //InputStream irs=new ByteArrayInputStream(strRes.getBytes(StandardCharsets.UTF_8));
                System.out.println(httpConnection.getContent().toString());
                Document document = builder.parse(httpConnection.getInputStream());
                System.out.print("Document Stream: " + document.toString());
                document.getDocumentElement().normalize();
                NodeList nList = document.getElementsByTagName("result");

                System.out.println("check3 " + nList.getLength());
                for (int i = 0; i < nList.getLength(); i++)
                {
                    System.out.println("Result value " + i + nList.item(i).getTextContent());
                }

                Node nNode = nList.item(0);

                Element eElement = (Element) nNode;

                NodeList addrsComponts = eElement.getElementsByTagName("address_component");

                int addrssCount = addrsComponts.getLength();
                String statename = "";
                for(int i=0;i<addrssCount;i++) {
                    // For each address component
                    Element addElement = (Element) addrsComponts.item(i);
                    NodeList types = addElement.getElementsByTagName("type");
                    // Check if first type is administrative_area_level_1
                    Element type = (Element) types.item(0);
                    if(type.getTextContent().equals("administrative_area_level_1"))
                    {
                        statename = addElement.getElementsByTagName("long_name").item(0).getTextContent();
                        return statename;
                    }
                }

                //Element statedetails = (Element) addrsComponts.item(addrssCount - 3); //Selecting second last address_cmponent in result to pick state

                //System.out.println("State of city Entered : " + statedetails.getElementsByTagName("long_name").item(0).getTextContent());

                //String stateCode = statedetails.getElementsByTagName("long_name").item(0).getTextContent();
                return statename;
            }
            catch (Exception e)
            {
                System.out.println("Exception inside getStateName");
                return "NA";
            }
        }

        return null;
    }

    private static
            int getCenterCode(String centerName) throws Exception
    {
        Connection c = null;
        Statement stmt = null;
        int StateCode = 0;
        try
        {
            Class.forName("org.postgresql.Driver");
            c = DriverManager.getConnection("jdbc:postgresql://localhost:5432/onion",
                    "postgres", "password");

            c.setAutoCommit(true);
            stmt = c.createStatement();

            String stateSelect = "Select * from centres WHERE centrename ilike ?";

            PreparedStatement stateSelectPS = c.prepareStatement(stateSelect);
            stateSelectPS.setString(1, centerName);

            ResultSet rs = stateSelectPS.executeQuery();

            if (rs.next())
            {

                StateCode = rs.getInt("centreid");
            }
            stateSelectPS.close();
            rs.close();

        }
        catch (Exception e)
        {
            System.err.println("Exception in stateCode fetch " + e.getMessage());
            throw e;
        }
        finally
        {
            c.close();
        }

        // System.out.println("State Code ----"+stateCode);
        return StateCode;
    }

    private static
            int getStateCode(String state) throws Exception
    {
        Connection c = null;
        Statement stmt = null;
        int stateCode = 0;
        try
        {
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

            if (!rs.next())
            {
                PreparedStatement ps = c.prepareStatement(stateInsert);
                ps.setString(1, state);

                ps.executeUpdate();
                ps.close();

                PreparedStatement stateSelPS = c.prepareStatement(stateSelect);
                stateSelPS.setString(1, state);

                ResultSet rs1 = stateSelPS.executeQuery();
                if (rs1.next())
                {
                    stateCode = rs1.getInt("StateCode");
                }
                stateSelPS.close();
                rs1.close();
            }
            else
            {
                stateCode = rs.getInt("StateCode");
            }
            stateSelectPS.close();
            rs.close();

        }
        catch (Exception e)
        {
            System.err.println("Exception in stateCode fetch " + e.getMessage());
            throw e;
        }
        finally
        {
            c.close();
        }

        // System.out.println("State Code ----"+stateCode);
        return stateCode;
    }

    private static
            int InsertIntoCenter(String centerName, int stateCode, String longitude, String latitude) throws Exception
    {
        Connection c = null;
        Statement stmt = null;
        int commodityCode = 0;
        try
        {
            Class.forName("org.postgresql.Driver");
            c = DriverManager.getConnection("jdbc:postgresql://localhost:5432/onion",
                    "postgres", "password");

            c.setAutoCommit(true);
            stmt = c.createStatement();
            String centerInsert = "Insert into centres(centrename,StateCode,longitude,latitude) Values(?,?,?,?)";

            String centerSelect = "Select * from centres WHERE centrename ilike ? AND StateCode=?";

            PreparedStatement centerSelectPS = c.prepareStatement(centerSelect);
            centerSelectPS.setString(1, centerName);
            centerSelectPS.setInt(2, stateCode);

            ResultSet rs = centerSelectPS.executeQuery();

            if (!rs.next())
            {
                PreparedStatement ps = c.prepareStatement(centerInsert);
                ps.setString(1, centerName);
                ps.setInt(2, stateCode);
                ps.setDouble(3, Double.parseDouble(longitude));
                ps.setDouble(4, Double.parseDouble(latitude));

                ps.executeUpdate();
                ps.close();

                PreparedStatement commSelPS = c.prepareStatement(centerSelect);
                commSelPS.setString(1, centerName);
                commSelPS.setInt(2, stateCode);

                ResultSet rs1 = commSelPS.executeQuery();
                if (rs1.next())
                {
                    commodityCode = rs1.getInt("centreid");
                }
                commSelPS.close();
                rs1.close();
            }
            else
            {
                commodityCode = rs.getInt("centreid");
            }
            centerSelectPS.close();
            rs.close();

        }
        catch (Exception e)
        {
            System.err.println("Exception in InsertIntocenter  " + e.getMessage());
            throw e;
        }
        finally
        {
            c.close();
        }
        //System.out.println("Commodity Code --"+commodityCode);
        return commodityCode;
    }

    private static
            void InsertIntoRetail(int centerCode, String price, Date dateOfData) throws Exception
    {
        Connection c = null;
        Statement stmt = null;
        try
        {
            Class.forName("org.postgresql.Driver");
            c = DriverManager.getConnection("jdbc:postgresql://localhost:5432/onion",
                    "postgres", "password");

            c.setAutoCommit(true);
            stmt = c.createStatement();

            String prepQuery = "Insert into retailoniondata Values(?,?,?)";

            PreparedStatement ps = c.prepareStatement(prepQuery);

            ps.setInt(2, centerCode);

            try
            {
                double pr = Double.parseDouble(price);
                ps.setDouble(3, pr);
            }
            catch (Exception e)
            {
                ps.setNull(3, java.sql.Types.DOUBLE);
            }

            ps.setDate(1, new java.sql.Date(dateOfData.getTime()));

            ps.executeUpdate();
            ps.close();
            stmt.close();
            c.close();

        }
        catch (Exception e)
        {
            System.err.println("Exception in InsertIntoRetail " + e.getMessage());
            throw e;

        }
    }

    private static
            String[] fetchLocation(String centerName, String stateName) throws MalformedURLException, IOException
    {
        boolean setProxy = true;
        String API_KEY = "AIzaSyBauH9z4UTKcc4kuUZ4_FBu4KUtfDbzIPk";
        int responseCode = 200;
        String api;

        api = "https://maps.googleapis.com/maps/api/geocode/xml?address=" + URLEncoder.encode(centerName + "," + stateName, "UTF-8") + "&sensor=true&key=" + API_KEY;

        System.out.println("API " + api);
        URL url = new URL(api);
        HttpURLConnection httpConnection = (HttpURLConnection) url.openConnection();

        if (setProxy)
        {
            // System.out.println("Setting proxy");
            Proxy proxy = new Proxy(Proxy.Type.HTTP, new InetSocketAddress("10.10.78.62", 3128));
            httpConnection = (HttpURLConnection) url.openConnection(proxy);
        }

        httpConnection.connect();
        responseCode = httpConnection.getResponseCode();
        if (responseCode == 200)
        {
            try
            {
                DocumentBuilder builder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
                //String strRes="<GeocodeResponse><status>OK</status><result><type>locality</type><type>political</type><formatted_address>Kanpur, Uttar Pradesh, India</formatted_address><address_component><long_name>Kanpur</long_name><short_name>Kanpur</short_name><type>locality</type><type>political</type></address_component><address_component><long_name>Kanpur Nagar</long_name><short_name>Kanpur Nagar</short_name><type>administrative_area_level_2</type><type>political</type></address_component><address_component><long_name>Uttar Pradesh</long_name><short_name>UP</short_name><type>administrative_area_level_1</type><type>political</type></address_component><address_component><long_name>India</long_name><short_name>IN</short_name><type>country</type><type>political</type></address_component><geometry><location><lat>26.4499230</lat><lng>80.3318736</lng></location><location_type>APPROXIMATE</location_type><viewport><southwest><lat>26.3512674</lat><lng>80.2087784</lng></southwest><northeast><lat>26.5430800</lat><lng>80.4679871</lng></northeast></viewport><bounds><southwest><lat>26.3512674</lat><lng>80.2087784</lng></southwest><northeast><lat>26.5430800</lat><lng>80.4679871</lng></northeast></bounds></geometry><place_id>ChIJb8QnsXBHnDkRQXu-nyoweBc</place_id></result><result><type>locality</type><type>political</type><formatted_address>Kanpur, Uttar Pradesh 209865, India</formatted_address><address_component><long_name>Kanpur</long_name><short_name>Kanpur</short_name><type>locality</type><type>political</type></address_component><address_component><long_name>Unnao</long_name><short_name>Unnao</short_name><type>administrative_area_level_2</type><type>political</type></address_component><address_component><long_name>Uttar Pradesh</long_name><short_name>UP</short_name><type>administrative_area_level_1</type><type>political</type></address_component><address_component><long_name>India</long_name><short_name>IN</short_name><type>country</type><type>political</type></address_component><address_component><long_name>209865</long_name><short_name>209865</short_name><type>postal_code</type></address_component><geometry><location><lat>26.3201324</lat><lng>80.5841155</lng></location><location_type>APPROXIMATE</location_type><viewport><southwest><lat>26.3125700</lat><lng>80.5787200</lng></southwest><northeast><lat>26.3243099</lat><lng>80.5892201</lng></northeast></viewport><bounds><southwest><lat>26.3125700</lat><lng>80.5787200</lng></southwest><northeast><lat>26.3243099</lat><lng>80.5892201</lng></northeast></bounds></geometry><place_id>ChIJsRP7YHRvnDkRg3c4ISL54Lo</place_id></result><result><type>locality</type><type>political</type><formatted_address>Kanpur, Madhya Pradesh 485331, India</formatted_address><address_component><long_name>Kanpur</long_name><short_name>Kanpur</short_name><type>locality</type><type>political</type></address_component><address_component><long_name>Satna</long_name><short_name>Satna</short_name><type>administrative_area_level_2</type><type>political</type></address_component><address_component><long_name>Madhya Pradesh</long_name><short_name>MP</short_name><type>administrative_area_level_1</type><type>political</type></address_component><address_component><long_name>India</long_name><short_name>IN</short_name><type>country</type><type>political</type></address_component><address_component><long_name>485331</long_name><short_name>485331</short_name><type>postal_code</type></address_component><geometry><location><lat>24.8739100</lat><lng>80.7824012</lng></location><location_type>APPROXIMATE</location_type><viewport><southwest><lat>24.8572700</lat><lng>80.7693900</lng></southwest><northeast><lat>24.8908600</lat><lng>80.7970400</lng></northeast></viewport><bounds><southwest><lat>24.8572700</lat><lng>80.7693900</lng></southwest><northeast><lat>24.8908600</lat><lng>80.7970400</lng></northeast></bounds></geometry><place_id>ChIJZwNDWEFigzkRm0FL4_-kOk0</place_id></result></GeocodeResponse>";
                //InputStream irs=new ByteArrayInputStream(strRes.getBytes(StandardCharsets.UTF_8));
                //System.out.println(httpConnection.getContent().toString());
                Document document = builder.parse(httpConnection.getInputStream());
                //System.out.print("Document Stream: " + document.toString());
                //System.out.println("check1");
                document.getDocumentElement().normalize();
                //System.out.println("check2");
                NodeList nList = document.getElementsByTagName("location");

                // Check if the mandi name given is invalid i.e. google is not able to recognize
                String output;
                Transformer transformer = TransformerFactory.newInstance().newTransformer();
                StreamResult result = new StreamResult(new StringWriter());
                DOMSource source = new DOMSource(document);
                transformer.transform(source, result);
                output = result.getWriter().toString();

                if (output.contains("ZERO_RESULTS"))
                {
                    System.out.println("Google Could Not Find: " + centerName + " " + stateName);
                    System.exit(0);
                }

                //System.out.println("check3 " + nList.getLength());
                for (int i = 0; i < nList.getLength(); i++)
                {
                    //System.out.println("Result value " + i + nList.item(i).getTextContent());
                }

                Node nNode = nList.item(0);

                Element eElement = (Element) nNode;

                NodeList lat = eElement.getElementsByTagName("lat");
                NodeList lng = eElement.getElementsByTagName("lng");

                Element latE = (Element) lat.item(0);
                Element lngE = (Element) lng.item(0);

                String result1[] = new String[2];
                result1[0] = lngE.getTextContent();
                result1[1] = latE.getTextContent();
                return result1;
            }
            catch (Exception e)
            {
                System.out.println("For " + centerName);
                System.out.println("Exception IN FETCHING LOCATION..." + e);
                System.out.println("---------------------------------------------------------------------");

            }
        }
        String result1[] = new String[2];
        result1[0] = "";
        result1[1] = "";
        return result1;
    }
}
