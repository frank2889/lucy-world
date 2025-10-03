# 🎯 GTM TRIGGERS SETUP GUIDE for Lucy World Search

## 📊 Custom Events Now Available

Your Lucy World Search app now sends these custom events to GTM:

### 🔍 **Search Events**
1. **`search_button_click`** - When user clicks search button
2. **`search_success`** - When search returns results
3. **`search_error`** - When search fails
4. **`keyword_search`** - General search tracking

### 👆 **User Interaction Events**
5. **`search_input_focus`** - When user clicks in search box
6. **`search_input_typing`** - When user types (3+ characters)
7. **`export_button_click`** - When user clicks export
8. **`data_export`** - When export completes

### 📈 **Engagement Events**
9. **`page_view`** - Page loads
10. **`scroll_depth`** - 25%, 50%, 75%, 90%
11. **`session_end`** - User leaves page

---

## 🛠️ GTM TRIGGER SETUP

### **Trigger 1: Search Button Click**
```
Trigger Type: Custom Event
Event Name: search_button_click
Fire On: All Custom Events

Use this trigger for:
- Google Analytics Events
- Conversion tracking
- A/B testing
```

### **Trigger 2: Successful Search**
```
Trigger Type: Custom Event
Event Name: search_success
Fire On: All Custom Events

Variables Available:
- {{Event - search_keyword}}
- {{Event - total_results}}
- {{Event - categories_found}}
- {{Event - response_time}}
```

### **Trigger 3: Search Input Focus**
```
Trigger Type: Custom Event
Event Name: search_input_focus
Fire On: All Custom Events

Use for:
- Engagement tracking
- User intent measurement
```

---

## 📋 GTM TAGS TO CREATE

### **Tag 1: GA4 Event - Search Button Click**
```
Tag Type: Google Analytics: GA4 Event
Configuration Tag: GA4-Configuration
Event Name: search_button_click
Parameters:
- search_keyword: {{Event - search_keyword}}
- button_id: {{Event - button_id}}
- keyword_length: {{Event - keyword_length}}

Trigger: search_button_click
```

### **Tag 2: GA4 Event - Search Success**
```
Tag Type: Google Analytics: GA4 Event
Configuration Tag: GA4-Configuration
Event Name: search_completed
Parameters:
- search_keyword: {{Event - search_keyword}}
- results_count: {{Event - total_results}}
- categories_count: {{Event - categories_found}}
- response_time_ms: {{Event - response_time}}

Trigger: search_success
```

### **Tag 3: GA4 Event - Export Action**
```
Tag Type: Google Analytics: GA4 Event
Configuration Tag: GA4-Configuration
Event Name: file_download
Parameters:
- file_name: keyword_research_export.csv
- keyword_count: {{Event - keyword_count}}
- export_format: {{Event - export_format}}

Trigger: data_export
```

---

## 🎯 CONVERSION GOALS TO SET UP

### **Goal 1: Search Completion**
- **Event**: `search_success`
- **Condition**: `total_results > 0`
- **Value**: Based on keyword count

### **Goal 2: Data Export**
- **Event**: `data_export`
- **Value**: Premium feature usage

### **Goal 3: High Engagement**
- **Event**: `scroll_depth`
- **Condition**: `depth = "75%"`

---

## 🔧 TESTING YOUR SETUP

### **1. GTM Preview Mode**
1. Go to GTM → Preview
2. Enter: `http://localhost:5000`
3. Perform a search
4. Check for these events:
   - `search_button_click`
   - `search_success`
   - `page_view`

### **2. Browser Console**
1. Open Developer Tools
2. Go to Console tab
3. Look for GTM events:
   ```
   📊 GTM Event: search_button_click {search_keyword: "SEO"}
   🔍 Search button clicked: SEO
   📊 GTM Event: search_success {total_results: 25}
   ```

### **3. GA4 DebugView**
1. Enable GA4 Debug mode
2. Perform searches
3. Check real-time events in GA4

---

## 📊 CUSTOM VARIABLES TO CREATE

### **Variable 1: Search Keyword**
```
Variable Type: Data Layer Variable
Data Layer Variable Name: search_keyword
```

### **Variable 2: Results Count**
```
Variable Type: Data Layer Variable
Data Layer Variable Name: total_results
```

### **Variable 3: Response Time**
```
Variable Type: Data Layer Variable
Data Layer Variable Name: response_time
```

---

## 🚀 NEXT STEPS

1. **Create GA4 Property** (if not exists)
2. **Set up triggers** in GTM using above configs
3. **Create tags** for each event type
4. **Test in Preview Mode**
5. **Publish GTM container**
6. **Verify in GA4 DebugView**

## 🎯 Pro Tips

- Use **Enhanced Ecommerce** for advanced keyword tracking
- Set up **Custom Dimensions** for search terms
- Create **Audiences** based on search behavior
- Use **Search Console integration** for complete SEO picture

Your Lucy World Search is now fully instrumented for advanced analytics! 🎉