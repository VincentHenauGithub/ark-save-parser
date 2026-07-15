from arkparse.enums import ArkMap, SubMap
from importlib.resources import files

def draw_heatmap(heatmap, map: ArkMap, submap: SubMap, map_fade: float = 0.7):
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    import numpy as np

    resolution = len(heatmap)
    mask = heatmap == 0
    package = 'arkparse.assets'
    name = f"{map.name}_{submap.value}.PNG" if submap else f"{map.name}.PNG"
    try:
        with open(files(package) / name, 'rb') as img_path:
            img = mpimg.imread(img_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find the image file for the map '{map.name}', you can add it to the assets folder in the arkparse package.")

    # Darken the image by multiplying pixel values (assuming float dtype, range [0,1])
    img_dark = img * map_fade
    plt.imshow(img_dark, extent=[0, resolution, 0, resolution], aspect='auto', origin='lower')
    plt.colorbar()

    is_all_zero = np.all(heatmap == 0)
    
    if not is_all_zero:
        heatmap_display = plt.imshow(heatmap, cmap='hot', interpolation='nearest', alpha=0.5, vmin=0.1)
        heatmap_display.set_alpha(np.where(mask, 0, 0.9))
    plt.show()