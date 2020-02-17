import table_users as users
import table_user_crops as user_crops
import table_crop_properties as crop_properties

def HumidityInRange(requiredRange,actualVal):
    minVal = list(requiredRange.split('-'))[0]
    maxVal = list(requiredRange.split('-'))[1]
    val = 0
    if (actualVal<maxVal) and (actualVal>minVal):
        val = 1 
    return val

def TemperatureInRange(requiredRange,actualVal):
    minVal = list(requiredRange.split('-'))[0]
    maxVal = list(requiredRange.split('-'))[1]
    val = 0
    if (actualVal<maxVal) and (actualVal>minVal):
        val = 1 
    return val

def RainfallInRange(requiredRange,actualVal):
    minVal = list(requiredRange.split('-'))[0]
    maxVal = list(requiredRange.split('-'))[1]
    val = 0
    if (actualVal<maxVal) and (actualVal>minVal):
        val = 1 
    return val

def LocationScore(locationDensity):
    val = (float(locationDensity)*0.3)**2
    val = -val
    return val

def CalculatePoints(crop_points,crop_prop,currentCondition):
    for crop in crop_points:
        humidity = HumidityInRange(crop_prop[crop][crop_properties.HUMIDITY],currentCondition[crop_properties.HUMIDITY])
        crop_points[crop] += humidity
        temperature = TemperatureInRange(crop_prop[crop][crop_properties.TEMPERATURE],currentCondition[crop_properties.TEMPERATURE])
        crop_points[crop] += temperature
        rainfall = RainfallInRange(crop_prop[crop][crop_properties.HUMIDITY],currentCondition[crop_properties.HUMIDITY])
        crop_points[crop] += rainfall
        locationDesnsityScore = LocationScore(currentCondition['locationDensity'])
        crop_points[crop] += locationDesnsityScore

    return crop_points