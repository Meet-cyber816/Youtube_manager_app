import sqlite3
import csv
import os
import argparse
import textwrap

conn = sqlite3.connect('youtube_videos.db')
cursor = conn.cursor()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            time TEXT NOT NULL,
            category TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

def list_video(order_by="id"):
    cursor.execute(f"SELECT * FROM videos ORDER BY {order_by}")
    videos = cursor.fetchall()
    print("\n" + "*" * 145)
    if videos:
        for row in videos:
            print(f"{row[0]}. video: {row[1]} | duration: {row[2]} | category: {row[3]} | added on: {row[4]}")
    else:
        print("No videos found.")
    print("*" * 145)

def add_video(name, time, category):
    cursor.execute("INSERT INTO videos (name, time, category) VALUES (?, ?, ?)", (name, time, category))
    conn.commit()
    print("Video added successfully!")

def batch_update_videos():
    video_ids = input("Enter video IDs to update (comma-separated): ").split(',')
    for vid in video_ids:
        try:
            vid = int(vid.strip())
            cursor.execute("SELECT * FROM videos WHERE id = ?", (vid,))
            video = cursor.fetchone()

            if video is None:
                print(f"No video found with ID {vid}. Skipping.")
                continue

            new_name = input(f"Enter new video name for ID {vid}: ")
            new_time = input(f"Enter new video duration (HH:MM:SS) for ID {vid}: ")
            new_category = input(f"Enter new video category for ID {vid}: ")

            cursor.execute("UPDATE videos SET name = ?, time = ?, category = ? WHERE id = ?", 
                           (new_name, new_time, new_category, vid))
            conn.commit()
            print(f"Video ID {vid} updated successfully!")

        except ValueError:
            print(f"Invalid ID: {vid}. Skipping.")

def batch_delete_videos():
    video_ids = input("Enter video IDs to delete (comma-separated): ").split(',')
    video_ids = [int(vid.strip()) for vid in video_ids if vid.strip().isdigit()]
    
    if not video_ids:
        print("No valid IDs provided.")
        return
    
    confirm = input("Are you sure you want to delete the selected videos? (yes/no): ")
    if confirm.lower() == 'yes':
        for vid in video_ids:
            cursor.execute("SELECT * FROM videos WHERE id = ?", (vid,))
            video = cursor.fetchone()
            
            if video is None:
                print(f"No video found with ID {vid}. Skipping.")
                continue

            cursor.execute("DELETE FROM videos WHERE id = ?", (vid,))
            conn.commit()
            print(f"Video ID {vid} deleted successfully.")
        
        cursor.execute("SELECT id FROM videos ORDER BY id")
        videos = cursor.fetchall()
        for index, (vid_id,) in enumerate(videos, start=1):
            cursor.execute("UPDATE videos SET id = ? WHERE id = ?", (index, vid_id))
        conn.commit()
        
        print("Selected videos deleted and IDs reordered.")
    else:
        print("Batch deletion canceled.")

def search_video(keyword):
    cursor.execute("SELECT * FROM videos WHERE category LIKE ?", ('%' + keyword + '%',))
    results = cursor.fetchall()
    print("\n" + "*" * 135)
    if results:
        for row in results:
            print(f"{row[0]}. video: {row[1]} | duration: {row[2]} | category: {row[3]} | added on: {row[4]}")
    else:
        print("No videos found with that keyword.")
    print("*" * 135)

def export_to_csv(filename="videos.csv"):
    cursor.execute("SELECT * FROM videos")
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([i[0] for i in cursor.description])
        writer.writerows(cursor.fetchall())
    print("Data exported successfully to", filename)

def main_menu():
    clear_screen()
    print("\n" + "#" * 120)
    print(" " * 45, "YouTube Manager App")
    print(" " * 45, "Creator: Meet Panchal")
    print("#" * 120)
    while True:
        print("\n")
        print("1. List videos")
        print("2. Add a video")
        print("3. Update videos")
        print("4. Delete videos")
        print("5. Search for a video")
        print("6. Export videos to CSV")
        print("7. Exit the app")
        
        choice = input("Enter your choice: ")
        
        clear_screen()
        
        if choice == '1':
            order = input("Sort by (id/name/time/date_added): ").strip()
            order_by = order if order in ["id", "name", "time", "date_added"] else "id"
            list_video(order_by)
        elif choice == '2':
            name = input("Enter video name: ")
            time = input("Enter video duration (HH:MM:SS): ")
            category = input("Enter video category: ")
            add_video(name, time, category)
        elif choice == '3':
            batch_update_videos()
        elif choice == '4':
            batch_delete_videos()
        elif choice == '5':
            keyword = input("Enter search keyword: ")
            search_video(keyword)
        elif choice == '6':
            filename = input("Enter filename for export (default 'videos.csv'): ").strip() or "videos.csv"
            export_to_csv(filename)
        elif choice == '7':
            break
        else:
            print("\nInvalid choice! Please try again.")

    conn.close()
    print("Goodbye!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
     description=textwrap.dedent("""
        YouTube Manager App: A powerful command-line tool for organizing and managing your personal YouTube video and playlist library. 
        This tool allows you to catalog video links, set custom categories, and access your videos or playlists directly from the terminal.

        Features:
        - Add Video and Playlist Links: Save both individual video and playlist links by naming them and setting custom categories. 
          This enables easy access to your saved content just by clicking the link.
        - Categorization: Organize videos and playlists with custom categories, allowing for a structured library tailored to your needs. 
          Use the search feature to quickly find content based on categories.
        - Search Functionality: Find videos and playlists effortlessly by searching within your chosen categories. This ensures you can 
          locate specific types of content without sifting through your entire library.
        - Sort and Export: Sort your collection by name, duration, or date added for easier viewing. Export all data to a CSV file for backup 
          or further analysis.

        Ideal for YouTube enthusiasts, educators, and content creators looking to maintain a streamlined library of videos and playlists, 
        this tool provides a quick and efficient way to manage your content without the need for a complex interface.
    """),
    epilog="Creator: Meet Panchal | Contact: meet24086@gmail.com",
    formatter_class=argparse.RawTextHelpFormatter
)
    args = parser.parse_args()
    main_menu()

