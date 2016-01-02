import pdfcrowd

try:
    # create an API client instance
    client = pdfcrowd.Client("jjo1", "ce78b1cd2aa07b4deafbe5f3c5fea965")

    # convert a web page and store the generated PDF into a pdf variable
    f = open("/Users/jonieva/tmp/test.pdf", "wb")
    pdf = client.convertURI('https://en.wikipedia.org/wiki/File:R_vs_L_Liver_by_CT.PNG', f)
    f.close()

    # convert an HTML string and save the result to a file
    output_file = open('html.pdf', 'wb')
    html="<head></head><body>My HTML Layout</body>"
    client.convertHtml(html, output_file)
    output_file.close()

    # convert an HTML file
    output_file = open('file.pdf', 'wb')
    client.convertFile('/path/to/MyLayout.html', output_file)
    output_file.close()

except pdfcrowd.Error, why:
    print('Failed: {}'.format(why))