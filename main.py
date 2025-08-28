import asyncio
import platform
from src.image_processor import remove_white_background
from src.animation import run_animation, create_demo_aquarium
import os

async def main():
    """Main function with error handling and demo options"""
    print("🐟 Aquatic Sim - Realistic Fish Animation")
    print("=" * 50)
    
    # File paths
    input_path = "assets/input/fish.jpg"
    output_path = "assets/output/fish_transparent.png"
    background_path = "assets/backgrounds/background.jpg"
    
    # Check if input file exists (for non-Pyodide environments)
    if platform.system() != "Emscripten" and not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}")
        print("Please place a fish image in aquatic_sim/assets/input/fish.jpg")
        return
    
    # Check if background file exists
    if platform.system() != "Emscripten" and not os.path.exists(background_path):
        print(f"⚠️ Background file not found: {background_path}")
        print("Using default background...")
        background_path = None
    
    print(f"🔄 Processing image: {input_path}")
    
    # Process image with multiple threshold attempts
    success = False
    thresholds = [240, 220, 200, 180, 160]
    
    for threshold in thresholds:
        print(f"Trying threshold: {threshold}")
        if platform.system() != "Emscripten" and remove_white_background(input_path, output_path, threshold=threshold):
            success = True
            print(f"✅ Successfully processed with threshold {threshold}")
            break
        elif platform.system() == "Emscripten":
            # Assume image is preprocessed for Pyodide
            success = True
            break
    
    if success:
        print(f"✅ Transparent image created: {output_path}")
        print("\nStarting animation...")
        
        # Ask user for demo preference
        print("\nSelect mode:")
        print("1. Standard Aquarium (800x600)")
        print("2. Advanced Demo (1200x800) - More fish")
        print("3. Custom - Specify number of fish")
        
        try:
            choice = input("\nChoice (1/2/3): ").strip()
            
            if choice == "1":
                print("🌊 Running Standard Aquarium...")
                await run_animation(background_path, output_path, fish_count=5)
            elif choice == "2":
                print("🌊 Running Advanced Demo...")
                await create_demo_aquarium(output_path, background_path)
            elif choice == "3":
                fish_count_input = input("Enter number of fish (1-20): ").strip()
                try:
                    fish_count = int(fish_count_input)
                    fish_count = max(1, min(20, fish_count))
                    print(f"🌊 Running aquarium with {fish_count} fish...")
                    await run_animation(background_path, output_path, fish_count=fish_count)
                except ValueError:
                    print("⚠️ Invalid number, running default mode...")
                    await run_animation(background_path, output_path, fish_count=5)
            else:
                print("🌊 Invalid choice, running default mode...")
                await run_animation(background_path, output_path, fish_count=5)
                
        except (ValueError, KeyboardInterrupt) as e:
            print(f"⚠️ Error: {e}")
            print("🌊 Running default mode...")
            await run_animation(background_path, output_path, fish_count=5)
    else:
        print("❌ Failed to process image with all thresholds.")
        print("Try:")
        print("1. Ensure the image has a clear white background")
        print("2. Use an image with good contrast")
        print("3. Try a different image format (e.g., PNG, JPG)")

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())