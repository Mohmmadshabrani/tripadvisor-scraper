def prepare_url(url, increment=10):
    url_parts = url.split("-or")
    if len(url_parts) > 1:
        current_number = int(url_parts[-1].split('-')[0])
        new_number = current_number + increment
        url_parts[-1] = f"{new_number}-" + "-".join(url_parts[-1].split('-')[1:])
        return "-or".join(url_parts)
    else:
        return url[:-5] + f"-or{increment}" + url[-5:]

# Example usage:
new_url = prepare_url()
print(new_url)
