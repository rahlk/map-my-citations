# Map My Citations

Map your citations create a annotated map and summary files of all your citations obtained from your Google Scholar page.

## Prerequisites 
- Create an account at https://serpapi.com/ to search through Google Scholar

## Usage

1. Install the citemap tool
         
         pip install --editable .
         
2. Get your API tokens from https://serpapi.com. 
3. Export the API token to a local variable

         export SERP_API_KEY=<your-api-key>
 
4. Invoke citemap with the following options:
```
Usage: citemap --author-id=<your-scholar-author-id> --serp-api-token=$SERP_API_KEY [--output-dir=<desired-save-location>]

 A small python app to generate and plot your Google Scholar citations.

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --author-id         TEXT  Your google scholar author id. For example, if your URL is https://scholar.google.com/citations?user=WGggocoAAAAJ&hl=en, then your author_id is the  part after user= and before &hl=en,      │
│                              i.e., WGggocoAAAAJ                                                                                                                                                                            │
│                              [required]                                                                                                                                                                                    │
│ *  --serp-api-token    TEXT  Your serp api token [required]                                                                                                                                                                │
│    --output-dir        PATH  The directory to save the outputs [default: /Users/rkrsn/workspace/pyCiteMap/etc/citemap_output]                                                                                              │
│    --help                    Show this message and exit.                                                                                                                                                                   │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```
   
## ⚠️ Caveat Emptor ⚠️

1. https://serpapi.com/ will charge you **$50** for making 5000 searches. For reference, 1 citation ≈ 1 search. So... yeah. 
I'll try to look for other alternatives like Selenium in the near future.      
