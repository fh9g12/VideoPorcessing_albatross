data = readtable('FLT2_4_data_right.csv');
angle = zeros(length(data.Frame),1);

ind = data.x0>data.x1;

angle(ind) = atan2d(-(data.y0(ind)-data.y1(ind)),(data.x0(ind)-data.x1(ind)));
ind = ~ind;
angle(ind) = atan2d(-(data.y1(ind)-data.y0(ind)),(data.x1(ind)-data.x0(ind)));
figure()
plot(angle)