/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package locationscript;

import java.io.IOException;
import java.io.StringWriter;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.InetSocketAddress;
import java.net.Proxy;
import java.net.URL;
import java.net.URLEncoder;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import javax.xml.xpath.XPathConstants;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

/**
 *
 * @author Kapil Thakkar
 */
class Place {

    String name;
    String state;

    public Place() {
        this.name = "";
        this.state = "";
    }

    public Place(String name, String state) {
        this.name = name;
        this.state = state;
    }
}

public class LocationScript {

    /**
     * @param args the command line arguments
     */
    public static boolean setProxy = false;
    public static String delimiter = "#";
    public static String API_KEY = "AIzaSyBauH9z4UTKcc4kuUZ4_FBu4KUtfDbzIPk";

    public static void main(String[] args) throws Exception {

        // Get the all centers and the mandi names
        ArrayList<Place> centerList = getCenters();
        ArrayList<Place> mandiList = getMandis();

        // Hash Map to save the location
        // KEY : Name
        // VALUE : Location
        HashMap<String, String> centerMap = new HashMap<String, String>();
        HashMap<String, String> mandiMap = new HashMap<String, String>();

        // Call API to get the location and sav it to the map
        for (Place mandi : mandiList) {
            boolean skip = locationPresent(mandi.name, "MANDIS");
            //System.out.println("Value of skip boolean : " + skip);
            
            if(mandi.name.equals("Nr. Co-op Central Bank(Ten),RBZ") || mandi.name.equals("Puwaha") || mandi.name.equals("Railway Over Bridge./Fatima,RBZ") || mandi.name.equals("Weekly Market Area,RBZ"))
                skip = true;

            if (!skip) {
                mandiMap.put(mandi.name, getLocation(mandi));
                setData(mandiMap, "MANDIS", "MandiName", "Location");
                mandiMap.clear();
            } else {
                //System.out.println("-----------------------------SKIP---------------------Mandi : " + mandi.name);
            }
        }

        System.out.println("****************************************************************************************");
        System.out.println("Done with Mandis.....");
        System.out.println("****************************************************************************************");

        for (Place center : centerList)
           centerMap.put(center.name, getLocation(center));
        // Set them in Database        
        setData(centerMap,"Center","CenterName","Location");
    }

    private static ArrayList<Place> getMandis() throws Exception {
        ArrayList mandiList = new ArrayList<Place>();
        Connection c = null;
        Statement stmt = null;
        int StateCode = 0;
        try {
            Class.forName("org.postgresql.Driver");
            c = DriverManager.getConnection("jdbc:postgresql://localhost:5432/Agriculture",
                    "postgres", "password");

            c.setAutoCommit(true);
            stmt = c.createStatement();

            String stateSelect = "select mandiname,state from mandis as m, states as s where m.statecode=s.statecode order by mandiname desc;";

            PreparedStatement stateSelectPS = c.prepareStatement(stateSelect);

            ResultSet rs = stateSelectPS.executeQuery();

            while (rs.next()) {
                Place m = new Place(rs.getString("MandiName"), rs.getString("state"));
                mandiList.add(m);
            }

            stateSelectPS.close();
            rs.close();
        } catch (Exception e) {
            System.err.println("Exception in stateCode fetch " + e.getMessage());
            throw e;
        } finally {
            c.close();
        }
        return mandiList;
    }

    private static ArrayList<Place> getCenters() throws Exception {
        ArrayList centerList = new ArrayList<Place>();
        Connection c = null;
        Statement stmt = null;
        try {
            Class.forName("org.postgresql.Driver");
            c = DriverManager.getConnection("jdbc:postgresql://localhost:5432/Agriculture",
                    "postgres", "password");

            c.setAutoCommit(true);
            stmt = c.createStatement();

            String stateSelect = "select centername,state from center as c, states as s where c.statecode = s.statecode";

            PreparedStatement stateSelectPS = c.prepareStatement(stateSelect);

            ResultSet rs = stateSelectPS.executeQuery();

            while (rs.next()) {
                Place p = new Place(rs.getString("CenterName"), rs.getString("state"));
                centerList.add(p);
            }
            stateSelectPS.close();
            rs.close();
        } catch (Exception e) {
            System.err.println("Exception in stateCode fetch " + e.getMessage());
            throw e;
        } finally {
            c.close();
        }
        return centerList;
    }

    private static String getLocation(Place centerName) throws UnsupportedEncodingException, ParserConfigurationException, SAXException, IOException {
        //
        if (centerName.name.contains("(")) {
            centerName.name = centerName.name.substring(0, centerName.name.indexOf("("));
        } 
            if (centerName.name.equals("Akiveedu")) {
            centerName.name = "Akividu";
        } else if (centerName.name.equals("Gooti")) {
            centerName.name = "Gooty";
        } else if (centerName.name.equals("Movva Hqs")) {
            centerName.name = "Movva";
        } else if (centerName.name.equals("Pidugurala")) {
            centerName.name = "Piduguralla";
        } else if (centerName.name.equals("Ungatur")) {
            centerName.name = "Unguturu";
        } else if (centerName.name.equals("A lot")) {
            centerName.name = "Alot";
        } else if (centerName.name.equals("Bandhabazar")) {
            centerName.name = "Bandha bazar";
        } else if (centerName.name.equals("Bohorihat")) {
            centerName.name = "Barpeta";
        } else if (centerName.name.equals("Anoop Shahar")) {
            centerName.name = "AnoopShahar";
        } else if (centerName.name.equals("Budalada")) {
            centerName.name = "Budhlada";
        } else if (centerName.name.equals("C.Camp,RBZ")) // RBZ id Raythu Bazar
        {
            centerName.name = "C-CAMP,KURNOOL";
        } else if (centerName.name.equals("Chengeri")) {
            centerName.name = "641669";
        } else if (centerName.name.equals("Dhamngaon-Railway")) {
            centerName.name = "Dhamngaon";
        } else if (centerName.name.equals("Dibbala Bazar,RBZ")) {
            centerName.name = "Prakasam";  // I think this is district, but I could not find anything
        } else if (centerName.name.equals("Erragadda,RBZ")) {
            centerName.name = "Erragadda";
        } else if (centerName.name.equals("Excise Colony,RBZ")) {
            centerName.name = "Excise Colony";
        } else if (centerName.name.equals("Falaknama,RBZ")) {
            centerName.name = "Falaknama";
        } else if (centerName.name.equals("Fatehkhanpet,RBZ")) {
            centerName.name = "524003";
        } else if (centerName.name.equals("Halia")) {
            centerName.name = "508202";
        } else if (centerName.name.equals("Jamkandorna")) {
            centerName.name = "Jamkandorana";
        } else if (centerName.name.equals("Kheragarh")) {
            centerName.name = "Khairagarh";
        } else if (centerName.name.equals("Mawiong Regulated Market")) {
            centerName.name = "Mawiong";
        } else if (centerName.name.equals("Momanbadodiya")) {
            centerName.name = "Moman badodiya";
        } else if (centerName.name.equals("Niralangar ")) {
            centerName.name = "Nirala nagar";  // My Judgement
        } else if (centerName.name.equals("Oddunchairum")) {
            centerName.name = "628501";  
        } else if (centerName.name.equals("Opp:Swami Theatre, ,RBZ,Guntur")) {
            centerName.name = "Guntur";  
        } else if (centerName.name.equals("Parshiwani")) {
            centerName.name = "Parshivni";  
        } else if (centerName.name.equals("Partaval")) {
            centerName.name = "Partawal";  
        } else if (centerName.name.equals("P. Ramacharyulu Park,RBZ")) {
            centerName.name = "Anantapur";  // I think its district // here : http://www.manarythubazar.com
        } else if (centerName.name.equals("Praswada")) {
            centerName.name = "Paraswada";  // I think its district // here : http://www.manarythubazar.com
        } else if (centerName.name.equals("Pullanga X Road,RBZ")) {
            centerName.name = "Nizamabad";  // I think its district // here : http://www.manarythubazar.com
        } else if (centerName.name.equals("Santhesargur")) {
            centerName.name = "Santhe sargur";  
        } else if (centerName.name.equals("Sevda")) {
            centerName.name = "466125";  
        } else if (centerName.name.equals("Suragana")) {
            centerName.name = "Surgana";  
        } else if (centerName.name.equals("Togguta")) {
            centerName.name = "502372";  
        } else if (centerName.name.equals("V.Kota Mkt.Yard")) {
            centerName.name = "V.Kota";  
        } 

        centerName.name = centerName.name.replace(",RBZ", "");
       
        int responseCode = 200;
        String api = "https://maps.googleapis.com/maps/api/geocode/xml?address=" + URLEncoder.encode(centerName.name + "," + centerName.state, "UTF-8") + "&sensor=true&key=" + API_KEY;

        System.out.println("API " + api);
        URL url = new URL(api);
        HttpURLConnection httpConnection = (HttpURLConnection) url.openConnection();

        if (setProxy) {
            // System.out.println("Setting proxy");
            Proxy proxy = new Proxy(Proxy.Type.HTTP, new InetSocketAddress("10.10.78.62", 3128));
            httpConnection = (HttpURLConnection) url.openConnection(proxy);
        }

        httpConnection.connect();
        responseCode = httpConnection.getResponseCode();
        if (responseCode == 200) {
            try {
                DocumentBuilder builder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
                
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

                if (output.contains("ZERO_RESULTS")) {
                    System.out.println("Google Could Not Find: " + centerName.name + " " + centerName.state);
                    System.exit(0);
                }

                //System.out.println("check3 " + nList.getLength());
                for (int i = 0; i < nList.getLength(); i++) {
                    //System.out.println("Result value " + i + nList.item(i).getTextContent());
                }

                Node nNode = nList.item(0);

                Element eElement = (Element) nNode;

                NodeList lat = eElement.getElementsByTagName("lat");
                NodeList lng = eElement.getElementsByTagName("lng");

                Element latE = (Element) lat.item(0);
                Element lngE = (Element) lng.item(0);

                //System.out.println("Center Name : " + centerName + " lat = " + latE.getTextContent() + "   lng = " + lngE.getTextContent());

                return latE.getTextContent() + delimiter + lngE.getTextContent();
            } catch (Exception e) {
                System.out.println("For " + centerName);
                System.out.println("Exception inside getStateName..." + e);
                System.out.println("---------------------------------------------------------------------");
                System.out.println("Calling Again... ");
                return getLocation(centerName);
                //System.out.println("---------------------------------------------------------------------");
                //return "NA";
            }
        }

        return null;
    }

    private static void setData(HashMap<String, String> map, String tableName, String conditionAttr, String updateAttr) throws Exception {
        Connection c = null;
        Statement stmt = null;
        int StateCode = 0;
        try {
            Class.forName("org.postgresql.Driver");
            c = DriverManager.getConnection("jdbc:postgresql://localhost:5432/Agriculture",
                    "postgres", "password");

            c.setAutoCommit(true);
            stmt = c.createStatement();

            // UPDATE tableName SET updateAttr = hashmap(i).getVal WHERE conditionAttr = hashmap(i).getKey;
            for (Map.Entry<String, String> entrySet : map.entrySet()) {
                String key = entrySet.getKey();
                String value = entrySet.getValue();
                String stateSelect = "UPDATE " + tableName + " SET " + updateAttr + "='" + value + "' WHERE " + conditionAttr + "='" + key + "'";
                //System.out.println("Query : " + stateSelect);
                PreparedStatement stateSelectPS = c.prepareStatement(stateSelect);
                stateSelectPS.executeUpdate();
                stateSelectPS.close();
            }
        } catch (Exception e) {
            System.err.println("Exception in stateCode fetch " + e.getMessage());
            throw e;
        } finally {
            c.close();
        }
    }

    private static boolean locationPresent(String mandi, String tableName) throws Exception {
        Connection c = null;
        Statement stmt = null;
        int CommQualityCode = 0;
        try {
            Class.forName("org.postgresql.Driver");
            c = DriverManager.getConnection("jdbc:postgresql://localhost:5432/Agriculture",
                    "postgres", "password");

            c.setAutoCommit(true);
            stmt = c.createStatement();

            String commQualitySelect = "Select location from " + tableName + " WHERE MandiName = '" + mandi + "'";
            //System.out.println("Query : " + commQualitySelect);
            PreparedStatement commQualitySelectPS = c.prepareStatement(commQualitySelect);

            ResultSet rs = commQualitySelectPS.executeQuery();

            if (rs.next()) {
                String loc = rs.getString("location");
                //System.out.println("Mandi: " + mandi + " Location : " + loc);
                if (loc == null) {
                    rs.close();
                    commQualitySelectPS.close();
                    return false;
                }
                if (loc.contains(delimiter)) {
                    //System.out.println("Location of " + mandi + " present in the table... SKIPPED");
                    rs.close();
                    commQualitySelectPS.close();
                    return true;
                } else {
                    rs.close();
                    commQualitySelectPS.close();
                    return false;
                }
            } else {
                rs.close();
                commQualitySelectPS.close();
                return false;
            }

        } catch (Exception e) {
            System.err.println("Exception in commodity Quality fetch " + e.getMessage());
            throw e;
        } finally {
            c.close();
        }

    }
}
