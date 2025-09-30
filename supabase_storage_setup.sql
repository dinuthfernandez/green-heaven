-- Supabase Storage Setup for Green Heaven Menu Images
-- Run this in your Supabase SQL Editor

-- Create storage bucket for menu images
INSERT INTO storage.buckets (id, name, public)
VALUES ('menu-images', 'menu-images', true)
ON CONFLICT (id) DO NOTHING;

-- Set up storage policies for public access to menu images
CREATE POLICY "Public Access" ON storage.objects FOR SELECT USING (bucket_id = 'menu-images');

-- Allow authenticated users to upload images (for staff/admin)
CREATE POLICY "Authenticated users can upload images" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'menu-images' AND auth.role() = 'authenticated');

-- Allow authenticated users to update images
CREATE POLICY "Authenticated users can update images" ON storage.objects FOR UPDATE USING (bucket_id = 'menu-images' AND auth.role() = 'authenticated');

-- Allow authenticated users to delete images
CREATE POLICY "Authenticated users can delete images" ON storage.objects FOR DELETE USING (bucket_id = 'menu-images' AND auth.role() = 'authenticated');

-- Update the menu items table to include image storage
CREATE TABLE IF NOT EXISTS public.menu_items (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    image_url TEXT,
    image_path TEXT,  -- Storage path in Supabase
    category TEXT DEFAULT 'Main Course',
    available BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on menu_items
ALTER TABLE public.menu_items ENABLE ROW LEVEL SECURITY;

-- Create policies for menu_items
CREATE POLICY "Anyone can view menu items" ON public.menu_items FOR SELECT USING (true);
CREATE POLICY "Authenticated users can manage menu items" ON public.menu_items FOR ALL USING (auth.role() = 'authenticated');

-- Enable real-time for menu_items
ALTER PUBLICATION supabase_realtime ADD TABLE public.menu_items;

-- Create trigger for updated_at
CREATE TRIGGER handle_menu_items_updated_at
    BEFORE UPDATE ON public.menu_items
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- Insert sample menu items with placeholder images
INSERT INTO public.menu_items (id, name, description, price, category, image_url) VALUES
('sri-curry', 'Traditional Sri Lankan Curry', 'Authentic curry with coconut milk, served with rice and papadum', 1250.00, 'Sri Lankan Specials', NULL),
('kottu-roti', 'Chicken Kottu Roti', 'Chopped flatbread stir-fried with chicken, vegetables and spices', 950.00, 'Sri Lankan Specials', NULL),
('hoppers', 'Egg Hoppers (2 pieces)', 'Traditional bowl-shaped pancakes with egg, served with sambol', 450.00, 'Appetizers', NULL),
('fish-curry', 'Fish Curry', 'Fresh fish in aromatic spices with coconut gravy', 1350.00, 'Sri Lankan Specials', NULL),
('pol-sambol', 'Pol Sambol', 'Traditional coconut relish with chili and lime', 250.00, 'Sides', NULL),
('papadum', 'Papadum (4 pieces)', 'Crispy lentil wafers', 200.00, 'Sides', NULL),
('mango-lassi', 'Mango Lassi', 'Fresh mango yogurt drink', 350.00, 'Beverages', NULL),
('thai-curry', 'Thai Green Curry', 'Spicy green curry with vegetables or chicken', 1150.00, 'International', NULL),
('fried-rice', 'Special Fried Rice', 'Wok-fried rice with egg and vegetables', 850.00, 'Rice & Noodles', NULL),
('garlic-naan', 'Garlic Naan', 'Fresh baked bread with garlic and herbs', 350.00, 'Breads', NULL)
ON CONFLICT (id) DO NOTHING;

SELECT 'Storage bucket and menu items table created successfully! 🍽️' as message;