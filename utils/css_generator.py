import os

def generate_css_variables_from_env(prefix="COLOR_", output_file="stylesheets/colors.css"):
    # css_lines = [":vars {"]
    css_lines = []
    for key, value in os.environ.items():
        if key.startswith(prefix):
            var_name = key[len(prefix):].lower().replace("_", "-")
            css_lines.append(f"  --{var_name}: #{value};")
    # css_lines.append("}")

    with open(output_file, "w") as f:
        f.write("\n".join(css_lines))
    print(f"✅ CSS file '{output_file}' generated with variables from env.")

# Exemple d'utilisation :
# os.environ["COLOR_PRIMARY"] = "#ff0000"
# os.environ["COLOR_SECONDARY"] = "#00ff00"
# generate_css_variables_from_env()
