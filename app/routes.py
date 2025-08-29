import pandas as pd
from flask import Blueprint, request, render_template, send_file
import io
from scraper import fetch_reel_data

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        reel_link = request.form.get("reel_link")
        file = request.files.get("file")
        filename_input = request.form.get("filename")  # <-- user entered filename

        links = []

        # ✅ Handle single link input
        if reel_link:
            links.append(reel_link.strip())

        # ✅ Handle uploaded file (read in memory, no saving)
        if file:
            if file.filename.endswith(".csv"):
                df = pd.read_csv(file)

                # ✅ Use "link" column if available, else fallback to first column
                if "link" in df.columns:
                    links.extend(df["link"].dropna().tolist())
                else:
                    links.extend(df.iloc[:, 0].dropna().tolist())

            elif file.filename.endswith(".txt"):
                links.extend([line.strip() for line in file.readlines() if line.strip()])
            else:
                return "Invalid file format. Upload CSV or TXT with reel links."

        if not links:
            return "No reel links provided."

        # ✅ Fetch data for each reel link
        data = []
        for link in links:
            try:
                info = fetch_reel_data(link)
                data.append(info)
            except Exception as e:
                data.append({"ReelLink": link, "Error": str(e)})

        # ✅ Convert to DataFrame
        df = pd.DataFrame(data)

        # ✅ Reorder columns in required order
        column_order = [
            "Platform",
            "ReelLink",
            "Username",
            "ProfileLink", 
            "Followers",
            "Likes",
            "Comments",
            "Shares",
            "Views",
        ]
        df = df.reindex(columns=column_order)

        # ✅ Save CSV in memory
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        # ✅ Use provided filename OR default
        save_name = filename_input.strip() if filename_input else "reels_output"
        if not save_name.lower().endswith(".csv"):
            save_name += ".csv"

        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name=save_name
        )

    return render_template("upload.html")
