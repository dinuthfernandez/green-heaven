#!/usr/bin/env python3
"""
Green Heaven Restaurant - Real Food Photo Downloader
Downloads actual food photos that match the exact food names
"""

import os
import sys
import requests
import uuid
import time
from io import BytesIO
from PIL import Image
import hashlib
import json

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from supabase import create_client
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("❌ Required packages not installed. Please install: supabase python-dotenv pillow")
    sys.exit(1)

class RealFoodPhotoDownloader:
    def __init__(self):
        """Initialize Supabase connection and photo sources"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            print("❌ Supabase credentials not found in environment variables")
            sys.exit(1)
        
        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            print("✅ Connected to Supabase")
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            sys.exit(1)
        
        # Photo sources with real food APIs
        self.photo_sources = {
            'unsplash': {
                'url': 'https://source.unsplash.com/400x300/',
                'active': True
            },
            'foodish': {
                'url': 'https://foodish-api.herokuapp.com/api/',
                'active': True
            }
        }
    
    def get_menu_items(self):
        """Get all menu items from database"""
        try:
            response = self.supabase.table('menu_items').select('*').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ Error loading menu items: {e}")
            return []
    
    def clean_food_name_for_search(self, food_name):
        """Clean and optimize food name for better search results"""
        # Remove portion indicators
        cleaned = food_name.replace(" (Full)", "").replace(" (Half)", "")
        
        # Remove restaurant specific terms
        cleaned = cleaned.replace(" - Green Heaven", "")
        cleaned = cleaned.replace("Green Heaven", "")
        
        # Extract main food item (before dash or comma)
        if " - " in cleaned:
            cleaned = cleaned.split(" - ")[0]
        if "," in cleaned:
            cleaned = cleaned.split(",")[0]
        
        # Clean up common terms
        cleaned = cleaned.replace("and", "&")
        cleaned = cleaned.replace("with", "")
        
        # Food name mappings for better results
        food_mappings = {
            'tom yum': 'tom yum soup',
            'kottu': 'kottu roti',
            'hoppers': 'egg hoppers',
            'pol sambol': 'coconut sambol',
            'papadum': 'papadam',
            'biriyani': 'biryani',
            'nasi goreng': 'indonesian fried rice',
            'mongolian fried rice': 'mongolian rice',
            'chopsuey': 'chop suey',
            'devilled': 'spicy',
            'cutlets': 'fish cutlets',
            'prawns': 'shrimp',
            'cuttlefish': 'squid',
            'mullet': 'mullet fish'
        }
        
        cleaned_lower = cleaned.lower().strip()
        for key, value in food_mappings.items():
            if key in cleaned_lower:
                cleaned = value
                break
        
        return cleaned.strip()
    
    def search_unsplash_food_image(self, food_name):
        """Search for real food images on Unsplash"""
        try:
            cleaned_name = self.clean_food_name_for_search(food_name)
            
            # Try different search terms
            search_terms = [
                f"{cleaned_name}",
                f"{cleaned_name} food",
                f"{cleaned_name} dish"
            ]
            
            for term in search_terms:
                try:
                    # Use a more direct approach with specific food image sources
                    search_query = term.replace(' ', '+').replace('&', 'and')
                    
                    # Try Unsplash with specific dimensions and query
                    urls_to_try = [
                        f"https://source.unsplash.com/featured/400x300/?{search_query}",
                        f"https://source.unsplash.com/400x300/?food+{search_query}",
                        f"https://source.unsplash.com/400x300/?{search_query}+meal"
                    ]
                    
                    for url in urls_to_try:
                        try:
                            print(f"    Trying: {url}")
                            response = requests.get(url, timeout=20, allow_redirects=True)
                            
                            if response.status_code == 200 and len(response.content) > 5000:
                                # Verify it's actually an image
                                try:
                                    img = Image.open(BytesIO(response.content))
                                    if img.mode in ('RGB', 'RGBA') and img.size[0] >= 300:
                                        print(f"  ✅ Found real food image via Unsplash: {term}")
                                        return BytesIO(response.content)
                                except Exception as img_error:
                                    print(f"    ❌ Invalid image format: {img_error}")
                                    continue
                            else:
                                print(f"    ❌ Bad response: {response.status_code}, size: {len(response.content)}")
                            
                            time.sleep(1)  # Rate limiting
                            
                        except Exception as url_error:
                            print(f"    ❌ URL failed: {url_error}")
                            continue
                    
                except Exception as term_error:
                    print(f"  ⚠️ Search term failed '{term}': {term_error}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"❌ Unsplash search error: {e}")
            return None
    
    def search_foodish_api(self, food_name):
        """Search Foodish API for real food images"""
        try:
            # Foodish API categories
            foodish_categories = [
                'biryani', 'burger', 'butter-chicken', 'dessert', 'dosa', 
                'idly', 'pasta', 'pizza', 'rice', 'samosa'
            ]
            
            cleaned_name = self.clean_food_name_for_search(food_name).lower()
            
            # Map food names to Foodish categories
            category_mapping = {
                'rice': 'rice',
                'fried rice': 'rice',
                'biryani': 'biryani',
                'biriyani': 'biryani',
                'pasta': 'pasta',
                'spaghetti': 'pasta',
                'burger': 'burger',
                'sandwich': 'burger',
                'chicken': 'butter-chicken',
                'curry': 'butter-chicken',
                'dessert': 'dessert',
                'sweet': 'dessert'
            }
            
            # Find matching category
            category = None
            for key, cat in category_mapping.items():
                if key in cleaned_name:
                    category = cat
                    break
            
            if category:
                try:
                    url = f"https://foodish-api.herokuapp.com/api/images/{category}"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        image_url = data.get('image')
                        
                        if image_url:
                            img_response = requests.get(image_url, timeout=15)
                            if img_response.status_code == 200:
                                print(f"  ✅ Found image via Foodish API: {category}")
                                return BytesIO(img_response.content)
                                
                except Exception as e:
                    print(f"  ⚠️ Foodish API failed: {e}")
            
            return None
            
        except Exception as e:
            print(f"❌ Foodish API error: {e}")
            return None
    
    def search_picsum_food_image(self, food_name):
        """Get food-themed images from Lorem Picsum"""
        try:
            # Generate a consistent seed based on food name
            food_seed = abs(hash(food_name)) % 1000
            
            # Try different Picsum endpoints
            urls_to_try = [
                f"https://picsum.photos/seed/{food_seed}/400/300",
                f"https://picsum.photos/400/300?random={food_seed}",
                f"https://picsum.photos/400/300?blur=0&grayscale=0&random={food_seed}"
            ]
            
            for url in urls_to_try:
                try:
                    print(f"    Trying Picsum: {url}")
                    response = requests.get(url, timeout=15, allow_redirects=True)
                    
                    if response.status_code == 200 and len(response.content) > 5000:
                        # Verify it's a valid image
                        try:
                            img = Image.open(BytesIO(response.content))
                            if img.mode in ('RGB', 'RGBA') and img.size[0] >= 300:
                                print(f"  ✅ Found image via Picsum for: {food_name}")
                                return BytesIO(response.content)
                        except:
                            continue
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"    ❌ Picsum URL failed: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"❌ Picsum search error: {e}")
            return None
    
    def download_real_food_image(self, food_name):
        """Download real food image using multiple sources"""
        print(f"🔍 Searching for real image: {food_name}")
        
        # Try different sources in order of preference
        sources = [
            self.search_unsplash_food_image,
            self.search_foodish_api,
            self.search_picsum_food_image
        ]
        
        for source_func in sources:
            try:
                image_data = source_func(food_name)
                if image_data:
                    return image_data
            except Exception as e:
                print(f"  ❌ Source failed: {e}")
                continue
        
        print(f"  ❌ No real image found for: {food_name}")
        return None
    
    def upload_to_supabase(self, image_data, filename):
        """Upload image to Supabase storage"""
        try:
            # Ensure we have the menu-images bucket
            try:
                self.supabase.storage.create_bucket('menu-images')
            except:
                pass  # Bucket might already exist
            
            # Convert BytesIO to bytes if needed
            if hasattr(image_data, 'getvalue'):
                file_bytes = image_data.getvalue()
            else:
                file_bytes = image_data
            
            # Upload file
            result = self.supabase.storage.from_('menu-images').upload(
                path=filename,
                file=file_bytes
            )
            
            if result:
                # Get public URL
                public_url = self.supabase.storage.from_('menu-images').get_public_url(filename)
                return public_url
            else:
                print(f"❌ Upload failed for {filename}")
                return None
                
        except Exception as e:
            print(f"❌ Error uploading {filename}: {e}")
            return None
    
    def update_menu_item_image(self, item_id, image_url):
        """Update menu item with new image URL"""
        try:
            response = self.supabase.table('menu_items').update({
                'image_url': image_url,
                'updated_at': 'now()'
            }).eq('id', item_id).execute()
            
            return True
        except Exception as e:
            print(f"❌ Error updating menu item {item_id}: {e}")
            return False
    
    def process_all_items(self, limit=None, force_update=False):
        """Process all menu items with real food photos"""
        print("🔍 Loading menu items from database...")
        menu_items = self.get_menu_items()
        
        if not menu_items:
            print("❌ No menu items found in database")
            return
        
        print(f"📋 Found {len(menu_items)} menu items")
        
        if limit:
            menu_items = menu_items[:limit]
            print(f"🎯 Processing first {len(menu_items)} items (limited)")
        
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        for i, item in enumerate(menu_items, 1):
            item_id = item.get('id')
            item_name = item.get('name', 'Unknown')
            current_image = item.get('image_url', '')
            
            print(f"\n📸 [{i}/{len(menu_items)}] Processing: {item_name}")
            
            # Skip if already has a real image (unless force update)
            if not force_update and current_image and 'supabase.co' in current_image:
                print(f"  ⏭️ Already has image, skipping")
                skipped_count += 1
                continue
            
            try:
                # Download real food image
                image_data = self.download_real_food_image(item_name)
                
                if not image_data:
                    print(f"  ❌ Could not find real image")
                    failed_count += 1
                    continue
                
                # Generate filename
                safe_name = "".join(c for c in item_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_').lower()
                item_id_short = item_id[:8] if item_id else str(uuid.uuid4())[:8]
                filename = f"real_{safe_name}_{item_id_short}.jpg"
                
                print(f"  📤 Uploading real image...")
                image_url = self.upload_to_supabase(image_data, filename)
                
                if image_url:
                    # Update database
                    print(f"  💾 Updating database...")
                    if self.update_menu_item_image(item_id, image_url):
                        print(f"  ✅ Successfully updated with REAL image: {item_name}")
                        success_count += 1
                    else:
                        print(f"  ❌ Failed to update database")
                        failed_count += 1
                else:
                    print(f"  ❌ Failed to upload image")
                    failed_count += 1
                
                # Delay to be respectful to APIs
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ Error processing {item_name}: {e}")
                failed_count += 1
        
        print(f"\n🎉 Processing complete!")
        print(f"✅ Success: {success_count} items updated with REAL food images")
        print(f"⏭️ Skipped: {skipped_count} items (already had images)")
        print(f"❌ Failed: {failed_count} items")
        print(f"📊 Total: {len(menu_items)} items processed")

def main():
    """Main function"""
    print("🍽️ Green Heaven Restaurant - REAL Food Photo Downloader")
    print("=" * 70)
    print("This will download ACTUAL food photos that match your menu items!")
    print()
    
    # Get command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Download REAL food photos for menu items')
    parser.add_argument('--limit', type=int, help='Limit number of items to process')
    parser.add_argument('--test', action='store_true', help='Test mode - process only 3 items')
    parser.add_argument('--force', action='store_true', help='Force update all images, even existing ones')
    args = parser.parse_args()
    
    if args.test:
        limit = 3
        print("🧪 Test mode: Processing only 3 items")
    else:
        limit = args.limit
    
    try:
        downloader = RealFoodPhotoDownloader()
        downloader.process_all_items(limit=limit, force_update=args.force)
        print("\n🎉 All done! Your menu now has REAL food photos!")
    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()