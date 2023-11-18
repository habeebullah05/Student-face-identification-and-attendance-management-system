with open(f'Attendance_July.csv', 'r+') as f:
    data = f.readlines()
    print(data)
    f.writelines("\nhello")