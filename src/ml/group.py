from src.etc import var

def unsuper(data, min_break, min_size):
    data.sort(key=lambda d: d[0])

    min_break = (data[-1][0] - data[0][0]) / min_break

    groups = []
    group = []
    nums = []

    while len(data) > 0:
        d = data.pop(0)
        x, _ = d

        group.append(d)
        nums.append(x)

        # Determine if break
        x1 = None if len(data) == 0 else data[0][0]

        if (x1 is None or (x != x1)) and (nums[-1] - nums[0] > min_break) and (len(nums) >= min_size):
            # New break
            groups.append(group)
            group = []
            nums = []
    
    # See if there is a remeinder
    if len(group) > 0:
        # It probably can not stand on its own, so add it to the last
        if len(groups) > 0:
            groups[-1] += group
        else:
            groups = [group]
    
    return groups




def merge(groups):
    proposal = []

    i = 0

    while i < len(groups) - 1:
        current = [g[0] for g in groups[i]]
        next = [g[0] for g in groups[i + 1]]
        both = current + next

        n1, n2 = len(current), len(next)
        var1, var2, var3 = var(current), var(next), var(both)

        # See if groups are dull
        # Dull = merge does not change variance
        if var3*0.95 <= (var1*n1 + var2*n2)/(n1+n2):
            proposal.append( groups[i] + groups[i+1] )
            i += 2
        else:
            proposal.append(groups[i])
            i += 1
    
    # Check if we need to add the last group
    # Note that if you merge the last 2 groups, then i = n
    if i == len(groups) - 1:
        proposal.append(groups[i])

    if len(proposal) < len(groups):
        return merge(proposal)
    else:
        return groups