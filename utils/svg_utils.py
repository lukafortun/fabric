import xml.etree.ElementTree as ET
import os

def recolor_svg(svg_str, new_color):
    tree = ET.ElementTree(ET.fromstring(svg_str))
    root = tree.getroot()

    for elem in root.iter():
        if 'fill' in elem.attrib:
            elem.set('fill', new_color)
        if 'stroke' in elem.attrib:
            elem.set('stroke', new_color)

    return ET.tostring(root, encoding='unicode')

def recolor_svgfile(svg_path, new_color):
    with open(svg_path, 'r') as file:
        svg_str = file.read()
    return recolor_svg(svg_str, new_color)

def recolor_svgfile_env(svg_path, env_color):
    color = "#" + os.environ.get(env_color, "ffffff" )
    return recolor_svgfile(svg_path, color)
    
