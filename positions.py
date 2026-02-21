
import sys
import json

# ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
DARK_GRAY = "\033[90m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"

INGREDIENT_COLORS = [YELLOW, BLUE, MAGENTA, CYAN, WHITE, RED]

def get_color(char):
    if char == '.': return GREEN
    if char == '#': return DARK_GRAY
    if char == '?': return RED
    if char.isalnum():
        return INGREDIENT_COLORS[ord(char) % len(INGREDIENT_COLORS)]
    return RESET

def create_grid(rows=10, cols=10, fill_char=' '):
    return [[fill_char for _ in range(cols)] for _ in range(rows)]

def print_grid(grid, item_name, count, legend):
    print(f"{BOLD}--- Layout for {item_name} ---{RESET}")
    print(f"Total Spots: {count}")
    print(f"Legend: {legend}")
    print("   " + " ".join([str(i) for i in range(10)]))
    for r in range(10):
        colored_row = [f"{get_color(char)}{char}{RESET}" for char in grid[r]]
        line = " ".join(colored_row)
        print(f"{r}  {line}")
    print("")

def get_symbols(made_of):
    # Assign symbols 0-9, A-Z to ingredients
    keys = sorted(list(made_of.keys()))
    mapping = {}
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    legend_parts = [f"{GREEN}.{RESET} : Crop"]
    
    for i, key in enumerate(keys):
        sym = chars[i] if i < len(chars) else "?"
        mapping[key] = sym
        legend_parts.append(f"{get_color(sym)}{sym}{RESET} : {key} ({made_of[key]})")
        
    return mapping, ", ".join(legend_parts)

def solve_layout(item_name, item_data, all_items):
    size = item_data.get("size", 1)
    made_of = item_data.get("made_of", {})
    destructive = item_data.get("destructive", False)
    explodes = item_data.get("explodes_on_harvest", False)
    
    mapping, legend = get_symbols(made_of)
    
    # Map counts and get sizes of ingredients
    symbol_counts = {}
    ingredient_sizes = {}
    for k, v in made_of.items():
        sym = mapping[k]
        symbol_counts[sym] = v
        # valid lookup if key exists
        if k in all_items:
            ingredient_sizes[sym] = all_items[k].get("size", 1)
        else:
            ingredient_sizes[sym] = 1
    
    grid = create_grid(fill_char=' ')
    spots = 0

    # DESTRUCTIVE LOGIC
    if destructive:
        center_r, center_c = 4, 4
        
        valid_indices = [center_r] # Only one spot
        
        pass

    # Special Case: Size 2 Crop with Size 3 Ingredient (e.g. PLANTBOY_ADVANCE)
    has_size_3 = any(s == 3 for s in ingredient_sizes.values())
    
    if size == 2 and has_size_3:
        # STRATEGY: Brute Force Backtracking to find MAX k placement
        # User requested "always max possible".
        
        # 1. Config
        # Crop P: 2x2
        # Ingredient S: 3x3 (Need 2)
        # Ingredient T: 1x1 (Need 6)
        
        s3_sym = None
        s3_count = 0
        others = []
        for sym, sz in ingredient_sizes.items():
            if sz == 3:
                s3_sym = sym
            else:
                others.extend([sym] * symbol_counts[sym])
        
        t_sym = '?'
        if len(others) > 0: t_sym = others[0]
        # Attempt to find actual T sym from library if 'others' is generic
        for sym, sz in ingredient_sizes.items():
             if sz == 1:
                 t_sym = sym
                 break
        
        valid_s_offsets = []
        for dr in range(-3, 3): # range sufficient to cover around
            for dc in range(-3, 3):
                # Check Overlap
                # S spans [dr, dr+2] x [dc, dc+2]
                # P spans [0, 1] x [0, 1]
                r_overlap = max(0, min(1, dr+2) - max(0, dr) + 1)
                c_overlap = max(0, min(1, dc+2) - max(0, dc) + 1)
                
                # Check intersection logic carefully
                # Overlap if lines intersect
                # rows 0,1. S rows dr, dr+1, dr+2.
                # intersect if dr <= 1 and dr+2 >= 0
                has_overlap = (dr <= 1 and dr+2 >= 0) and (dc <= 1 and dc+2 >= 0)
                
                if not has_overlap:
                    # Check adjacency (dist 1)
                    # Expand P by 1: [-1, 2] x [-1, 2]
                    # if S intersects expansion, it touches.
                    touches = (dr <= 2 and dr+2 >= -1) and (dc <= 2 and dc+2 >= -1)
                    if touches:
                        valid_s_offsets.append((dr, dc))

        def can_place_s(g, sr, sc, sym):
            if sr < 0 or sc < 0 or sr+2 >= 10 or sc+2 >= 10: return False
            for r in range(sr, sr+3):
                for c in range(sc, sc+3):
                    if g[r][c] != ' ' and g[r][c] != sym:
                        return False
            return True

        def place_s(g, sr, sc, sym):
            for r in range(sr, sr+3):
                for c in range(sc, sc+3):
                    g[r][c] = sym
                    
        def remove_s(g, sr, sc):
             # This is tricky with overlaps. 
             # We should clone grid or use a rigorous state.
             # Since P3 is slow, grid copy is OK.
             pass

        def get_neighbors_p(pr, pc):
            # Return all adjacent cells to 2x2 P
            # Top: (pr-1, pc), (pr-1, pc+1)
            # Bottom: (pr+2, pc), (pr+2, pc+1)
            # Left: (pr, pc-1), (pr+1, pc-1)
            # Right: (pr, pc+2), (pr+1, pc+2)
            # Corners: (pr-1, pc-1), (pr-1, pc+2), (pr+2, pc-1), (pr+2, pc+2)
            candidates = []
            # Top row
            candidates.extend([(pr-1, c) for c in range(pc-1, pc+3)])
            # Bottom row
            candidates.extend([(pr+2, c) for c in range(pc-1, pc+3)])
            # Sides
            candidates.append((pr, pc-1)); candidates.append((pr, pc+2))
            candidates.append((pr+1, pc-1)); candidates.append((pr+1, pc+2))
            return candidates

        best_grid = None
            
        def solve(k, idx, current_grid):
            nonlocal best_grid
            if k == 0:
                best_grid = [row[:] for row in current_grid]
                return True
            
            # Try to place 1 crop
            # Iterate positions
            for i in range(idx, 81): # 0..8, 0..8 -> max index 88? 9*9=81 positions (0..8)
                pr, pc = divmod(i, 9) # 9 cols relevant for top-left
                if pr > 8 or pc > 8: continue # should be covered by range but just safe
                
                # Check P fit
                p_fits = True
                for r in range(pr, pr+2):
                    for c in range(pc, pc+2):
                        if current_grid[r][c] != ' ':
                            p_fits = False; break
                    if not p_fits: break
                
                if p_fits:
                    # Place P
                    # We need to backtrack P too, so copy grid or meticulous undo
                    # Copying is safer for prototyping
                    next_grid = [row[:] for row in current_grid]
                    for r in range(pr, pr+2):
                        for c in range(pc, pc+2):
                            next_grid[r][c] = '.'
                            
                    # satisfy S (need 2)
                    # Iterate couples of S?
                    # Or nested recursion?
                    # Let's simple Loop for S1, S2
                    
                    found_s_config = False
                    
                    # We need 2 SNOOZLINGs
                    # Get valid absolute S positions
                    possible_s = []
                    for dr, dc in valid_s_offsets:
                        sr, sc = pr+dr, pc+dc
                        if can_place_s(next_grid, sr, sc, s3_sym):
                            possible_s.append((sr, sc))
                            
                    # Try pairs
                    import itertools
                    
                    for s1, s2 in itertools.combinations(possible_s, 2):
                        # Check S1 S2 overlap
                        s1r, s1c = s1
                        s2r, s2c = s2
                        # Quick overlap check
                        overlap = (abs(s1r - s2r) < 3) and (abs(s1c - s2c) < 3)
                        if overlap: continue

                        temp_g = [row[:] for row in next_grid]
                        place_s(temp_g, s1r, s1c, s3_sym)
                        place_s(temp_g, s2r, s2c, s3_sym)
                        
                        # Check T requirements (6 T's)
                        neighbors = get_neighbors_p(pr, pc)
                        t_count = 0
                        t_spots = []
                        
                        valid_t = True
                        for nr, nc in neighbors:
                             if 0 <= nr < 10 and 0 <= nc < 10:
                                 cell = temp_g[nr][nc]
                                 if cell == t_sym:
                                     t_count += 1
                                 elif cell == s3_sym:
                                     pass # is S
                                 elif cell == ' ':
                                     t_spots.append((nr, nc))
                                 elif cell == '.':
                                     pass # self? (should not happen in neighbors)
                                 else:
                                     pass # blocked
                                    
                        needed = 6 - t_count
                        if needed <= len(t_spots):
                            # Place T's
                            for _ in range(needed):
                                tr, tc = t_spots.pop()
                                temp_g[tr][tc] = t_sym
                            # Success for this crop!
                            if solve(k-1, i+1, temp_g):
                                return True
                            # Else, try next S pair
                        
                    # If no S pair worked, this P placement fails
            
            return False

        # Try k from 4 down to 1
        for k in range(4, 0, -1):
            if solve(k, 0, grid):
                grid[:] = best_grid[:] # Update grid in place
                spots = k # spots is count of crops?
                spots = sum(row.count('.') for row in grid)
                break

    # Standard Algorithms with Optional Single-Spot Override
    
    elif size == 3:
        pool = []
        for s, c in symbol_counts.items(): pool.extend([s]*c)
        if len(pool) < 16: pool.extend(['?'] * (16 - len(pool)))
        
        offsets = []
        for dc in range(-1, 4): offsets.append((-1, dc))
        for dr in range(0, 3): offsets.append((dr, 3))
        for dc in range(3, -2, -1): offsets.append((3, dc))
        for dr in range(2, -1, -1): offsets.append((dr, -1))
        
        if destructive:
            valid_indices = [4] # Place one at 4,4
        else:
            valid_indices = [1, 5]

        for r in valid_indices:
            for c in valid_indices:
                # Place Crop
                for dr in range(3):
                    for dc in range(3):
                        grid[r+dr][c+dc] = '.'
                spots += 1
                
                # Place Ingredients
                for i, (or_, oc) in enumerate(offsets):
                    sym = pool[i % len(pool)]
                    gr, gc = r + or_, c + oc
                    if 0 <= gr < 10 and 0 <= gc < 10:
                        if grid[gr][gc] == ' ' or grid[gr][gc] == sym:
                            grid[gr][gc] = sym

    elif size == 2:
        offsets = []
        for dc in range(-1, 3): offsets.append((-1, dc))
        for dr in range(0, 2): offsets.append((dr, 2))
        for dc in range(2, -2, -1): offsets.append((2, dc))
        for dr in range(1, -1, -1): offsets.append((dr, -1))

        # Organize pool to satisfy adjacency symmetry including corners
        # Corners: 0, 3, 6, 9 must be same
        # Pairs: (1,8), (2,7), (4,11), (5,10)
        
        final_pool = [None] * 12
        corners = [0, 3, 6, 9]
        pairs = [(1,8), (2,7), (4,11), (5,10)]
        
        counts = dict(symbol_counts)
        
        # 1. Fill Corners
        corner_sym = None
        if counts:
            best_sym = max(counts, key=counts.get)
            if counts[best_sym] >= 4:
                corner_sym = best_sym
                counts[corner_sym] -= 4
                for idx in corners: final_pool[idx] = corner_sym
        
        # 2. Fill Pairs
        pair_idx = 0
        leftovers = []
        
        # Sort remaining counts
        sorted_remaining = sorted(counts.items(), key=lambda x: x[1], reverse=True)

        for sym, count in sorted_remaining:
            num_pairs = count // 2
            rem = count % 2
            for _ in range(num_pairs):
                if pair_idx < len(pairs):
                    i1, i2 = pairs[pair_idx]
                    final_pool[i1] = sym
                    final_pool[i2] = sym
                    pair_idx += 1
                else:
                    leftovers.extend([sym, sym])
            if rem > 0:
                leftovers.append(sym)
                
        # Fill remaining
        for i in range(12):
            if final_pool[i] is None:
                if leftovers:
                    final_pool[i] = leftovers.pop(0)
                else:
                    # Try to fill from counts if we skipped corner logic or ran out
                    # (Should be covered by leftovers logic but just in case)
                    found = False
                    for s, c in counts.items():
                        if c > 0:
                            final_pool[i] = s
                            counts[s] -= 1
                            found = True
                            break
                    if not found:
                        final_pool[i] = '?'
        
        pool = final_pool

        if destructive:
             valid_indices = [4] # Place one at 4,4
        else:
             valid_indices = [1, 4, 7]
             
        for r in valid_indices:
            for c in valid_indices:
                # Place Crop
                for dr in range(2):
                    for dc in range(2):
                        grid[r+dr][c+dc] = '.'
                spots += 1
                
                for i, (or_, oc) in enumerate(offsets):
                    sym = pool[i]
                    gr, gc = r + or_, c + oc
                    if 0 <= gr < 10 and 0 <= gc < 10:
                        # Only place if empty or same symbol (to allow sharing)
                        if grid[gr][gc] == ' ' or grid[gr][gc] == sym:
                            grid[gr][gc] = sym

    elif size == 1:
        pool = []
        # Create a list of (symbol, count) for sorting
        counts_list = []
        for s, c in symbol_counts.items():
            pool.extend([s]*c)
            counts_list.append([s, c])
        
        total_ingredients = len(pool)
        
        has_size_2_ing = any(sz == 2 for sz in ingredient_sizes.values())
        
        if has_size_2_ing:
            sym_2 = [s for s, sz in ingredient_sizes.items() if sz == 2]
            sym_1 = [s for s, sz in ingredient_sizes.items() if sz == 1]
            main_sym_2 = sym_2[0] if sym_2 else '?'
            v_sym = sym_1[0] if len(sym_1) > 0 else '?'
            h_sym = sym_1[1] if len(sym_1) > 1 else v_sym

            if destructive:
                valid_indices = [4]
            else:
                valid_indices = [2, 7]
            
            valid_offsets = [
                # Top-Left 2x2
                (-2,-2), (-2,-1), (-1,-2), (-1,-1),
                # Top-Right 2x2
                (-2,1), (-2,2), (-1,1), (-1,2),
                # Bottom-Left 2x2
                (1,-2), (1,-1), (2,-2), (2,-1),
                # Bottom-Right 2x2
                (1,1), (1,2), (2,1), (2,2),
                # Vertical adj
                (-1,0), (1,0),
                # Horizontal adj
                (0,-1), (0,1)
            ]

            for r in valid_indices:
                for c in valid_indices:
                    grid[r][c] = '.'
                    spots += 1
                    for dr, dc in valid_offsets:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 10 and 0 <= nc < 10:
                            if grid[nr][nc] == ' ':
                                if abs(dr) >= 1 and abs(dc) >= 1:
                                    grid[nr][nc] = main_sym_2
                                elif dc == 0:
                                    grid[nr][nc] = v_sym
                                elif dr == 0:
                                    grid[nr][nc] = h_sym

        elif total_ingredients > 4 or explodes:
            
            # Sort by count desc
            counts_list.sort(key=lambda x: x[1], reverse=True)
            
            final_pool = [None] * 8
            groups = [
                [0, 2, 4, 6], # Corners (4)
                [1, 5],       # Verts (2)
                [3, 7]        # Horz (2)
            ]
            
            # Fill groups
            for group in groups:
                # Find a symbol that can satisfy this group
                found_s = None
                for item in counts_list:
                    if item[1] >= len(group):
                        found_s = item[0]
                        item[1] -= len(group)
                        break
                
                if found_s:
                    for idx in group:
                        final_pool[idx] = found_s
                else:
                    # Fill fragmented
                    for idx in group:
                        # Find any available
                        found_any = False
                        for item in counts_list:
                            if item[1] > 0:
                                final_pool[idx] = item[0]
                                item[1] -= 1
                                found_any = True
                                break
                        if not found_any:
                            final_pool[idx] = '?'
            
            pool = final_pool
            
            offsets = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
            
            if destructive:
                 # Place at 5,5
                 valid_indices = [5]
            else:
                 valid_indices = [1, 3, 5, 7]

            # Check symmetries for optimization
            h_swap = pool[3] != pool[7]
            v_swap = pool[1] != pool[5]

            for r_i, r in enumerate(valid_indices):
                for c_i, c in enumerate(valid_indices):
                    # Determine pool for this spot to resolve conflicts
                    cur_pool = list(pool)
                    
                    if h_swap and (c_i % 2 == 1):
                        cur_pool[3], cur_pool[7] = cur_pool[7], cur_pool[3]
                    
                    if v_swap and (r_i % 2 == 1):
                        cur_pool[1], cur_pool[5] = cur_pool[5], cur_pool[1]

                    grid[r][c] = '.'
                    spots += 1
                    for i, (or_, oc) in enumerate(offsets):
                         sym = cur_pool[i % len(cur_pool)]
                         gr, gc = r + or_, c + oc
                         if 0 <= gr < 10 and 0 <= gc < 10:
                             grid[gr][gc] = sym
        else:
            # 4-Neighbor
            syms = sorted(list(set(pool))) 
            
            if destructive:
                # Single spot at 5,5
                grid[5][5] = '.'
                spots = 1
                # Fill Neighbors
                neighbors = [(4,5), (6,5), (5,4), (5,6)]
                for i, (nr, nc) in enumerate(neighbors):
                     if len(syms) > 0:
                         grid[nr][nc] = syms[i % len(syms)]
                     else:
                         grid[nr][nc] = '?'
            else:
                for r in range(1, 9):
                    for c in range(1, 9):
                        if (r + c) % 2 == 0:
                            grid[r][c] = '.'
                            spots += 1
                for r in range(10):
                    for c in range(10):
                        if grid[r][c] == ' ':
                            if len(syms) >= 2:
                                if r % 2 == 0: grid[r][c] = syms[0]
                                else: grid[r][c] = syms[1]
                            elif len(syms) == 1: grid[r][c] = syms[0]
                            else: grid[r][c] = '?'
    
    # Post-process
    for r in range(10):
        for c in range(10):
            if grid[r][c] == ' ':
                grid[r][c] = '#'

    return grid, spots, legend

def main(args):
    priority = None
    if len(args) > 0:
        priority = args
    try:
        with open('items.json', 'r', encoding='utf-8') as f:
            items = json.load(f)
    except Exception as e:
        print(f"Error loading items.json: {e}")
        return

    print("Generating Symbolized Layouts...\n")
    if not priority:
        priority = ["NOCTILUME", "SNOOZLING", "SCOURROOT", "WITHERBLOOM", "DUSTGRAIN", "ZOMBUD", "ASHWREATH", "CHORUS_FRUIT", "PLANTBOY_ADVANCE"]
    
    for name in priority:
        if name in items:
            grid, count, legend = solve_layout(name, items[name], items)
            print_grid(grid, name, count, legend)

if __name__ == "__main__":
    main(sys.argv[1:])
