with open(r"e:\Pragnesh_Mutual_Fund\Main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1
old1 = "styled_display_df = display_df.style.apply(highlight_total, axis=1)"
new1 = """styled_display_df = display_df.style.apply(highlight_total, axis=1)
                            if "AUM" in display_df.columns:
                                styled_display_df = styled_display_df.format({"AUM": format_indian_currency}, na_rep="")"""
content = content.replace(old1, new1)

# 2
old2 = "styled_display_df = display_df.style.apply(highlight_and_color, axis=1)"
new2 = """styled_display_df = display_df.style.apply(highlight_and_color, axis=1)
            if "AUM" in display_df.columns:
                styled_display_df = styled_display_df.format({"AUM": format_indian_currency}, na_rep="")"""
content = content.replace(old2, new2)

# 3
old3 = """        except AttributeError:
            styled_df = merged_scheme.style.applymap(color_cells_quartile, subset=[c for c in required_periods if c in merged_scheme.columns])"""
new3 = """        except AttributeError:
            styled_df = merged_scheme.style.applymap(color_cells_quartile, subset=[c for c in required_periods if c in merged_scheme.columns])
        if "AUM" in merged_scheme.columns:
            styled_df = styled_df.format({"AUM": format_indian_currency}, na_rep="")"""
content = content.replace(old3, new3)

# 4
old4 = """            except AttributeError:
                detail_styled = detail_merged.style.applymap(color_cells_quartile, subset=[c for c in required_periods if c in detail_merged.columns])"""
new4 = """            except AttributeError:
                detail_styled = detail_merged.style.applymap(color_cells_quartile, subset=[c for c in required_periods if c in detail_merged.columns])
            if "AUM" in detail_merged.columns:
                detail_styled = detail_styled.format({"AUM": format_indian_currency}, na_rep="")"""
content = content.replace(old4, new4)


with open(r"e:\Pragnesh_Mutual_Fund\Main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Applied Styler formatting to UI.")
