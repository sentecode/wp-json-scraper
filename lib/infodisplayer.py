"""
Copyright (c) 2018-2020 Mickaël "Kilawyn" Walter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import html
import csv
from datetime import datetime

from lib.console import Console

class InfoDisplayer:
    """
    Static class to display information for different categories
    """

    @staticmethod
    def display_basic_info(information):
        """
        Displays basic information about the WordPress instance
        param information: information as a JSON object
        """
        print()

        if 'name' in information.keys():
            print("Site name: %s" % html.unescape(information['name']))

        if 'description' in information.keys():
            print("Site description: %s" %
                  html.unescape(information['description']))

        if 'home' in information.keys():
            print("Site home: %s" % html.unescape(information['home']))

        if 'gmt_offset' in information.keys():
            timezone_string = ""
            gmt_offset = str(information['gmt_offset'])
            if '-' not in gmt_offset:
                gmt_offset = '+' + gmt_offset
            if 'timezone_string' in information.keys():
                timezone_string = information['timezone_string']
            print("Site Timezone: %s (GMT%s)" % (timezone_string, gmt_offset))

        if 'namespaces' in information.keys():
            print('Namespaces (API provided by addons):')
            ns_ref = {}
            try:
                ns_ref_file = open("lib/plugins/plugin_list.csv", "rt")
                ns_ref_reader = csv.reader(ns_ref_file)
                for row in ns_ref_reader:
                    desc = None
                    url = None
                    if len(row) > 1 and len(row[1]) > 0:
                        desc = row[1]
                    if len(row) > 2 and len(row[2]) > 0:
                        url = row[2]
                    ns_ref[row[0]] = {"desc": desc, "url": url}
                ns_ref_file.close()
            except:
                Console.log_error("Could not load namespaces reference file")
            for ns in information['namespaces']:
                tip = ""
                if ns in ns_ref.keys():
                    if ns_ref[ns]['desc'] is not None:
                        if tip == "":
                            tip += " - "
                        tip += ns_ref[ns]['desc']
                    if ns_ref[ns]['url'] is not None:
                        if tip == "":
                            tip += " - "
                        tip += " - " + ns_ref[ns]['url']
                print('    %s%s' % (ns, tip))

        # TODO, dive into authentication
        print()

    @staticmethod
    def display_namespaces(information, details=False):
        """
            Displays namespace list of the WordPress API

            :param information: information as a JSON object
            :param details: unused, available for compatibility purposes
        """
        print()
        if information is not None:
            for ns in information:
                print("* %s" % ns)
        print()

    @staticmethod
    def display_endpoints(information):
        """
        Displays endpoint documentation of the WordPress API
        param information: information as a JSON object
        """
        print()

        if 'routes' not in information.keys():
            Console.log_error("Did not find the routes for endpoint discovery")
            return None

        for url, route in information['routes'].items():
            print("%s (Namespace: %s)" % (url, route['namespace']))
            for endpoint in route['endpoints']:
                methods = "    "
                first = True
                for method in endpoint['methods']:
                    if first:
                        methods += method
                        first = False
                    else:
                        methods += ", " + method
                print(methods)
                if len(endpoint['args']) > 0:
                    for arg, props in endpoint['args'].items():
                        required = ""
                        if props['required']:
                            required = " (required)"
                        print("        " + arg + required)
                        if 'type' in props.keys():
                            print("            type: " + str(props['type']))
                        if 'default' in props.keys():
                            print("            default: " +
                                  str(props['default']))
                        if 'enum' in props.keys():
                            allowed = "            allowed values: "
                            first = True
                            for val in props['enum']:
                                if first:
                                    allowed += val
                                    first = False
                                else:
                                    allowed += ", " + val
                            print(allowed)
                        if 'description' in props.keys():
                            print("            " + str(props['description']))
            print()

    @staticmethod
    def display_posts(information, orphan_comments=[], details=False):
        """
        Displays posts published on the WordPress instance
        param information: information as a JSON object
        """
        print()
        date_format = "%Y-%m-%dT%H:%M:%S-%Z"
        for post in information:
            if post is not None:
                line = ""
                if 'id' in post.keys():
                    line += "ID: %d" %post['id']
                if 'title' in post.keys():
                    line += " - " + html.unescape(post['title']['rendered'])
                if 'date_gmt' in post.keys():
                    date_gmt = datetime.strptime(post['date_gmt'] +
                                                "-GMT", date_format)
                    line += " on %s" % \
                            date_gmt.strftime("%d/%m/%Y at %H:%M:%S")
                if 'link' in post.keys():
                    line += " - " + post['link']
                if details:
                    if 'slug' in post.keys():
                        line += "\nSlug: " + post['slug']
                    if 'status' in post.keys():
                        line += "\nStatus: " + post['status']
                    if 'author' in post.keys():
                        line += "\nAuthor ID: %d" % post['author']
                    if 'comment_status' in post.keys():
                        line += "\nComment status: " + post['comment_status']
                    if 'template' in post.keys() and len(post['template']) > 0:
                        line += "\nTemplate: " + post['template']
                    if 'categories' in post.keys() and len(post['categories']) > 0:
                        line += "\nCategory IDs: "
                        for cat in post['categories']:
                            line += "%d, " % cat
                        line = line[:-2]
                    if 'excerpt' in post.keys():
                        line += "\nExcerpt: "
                        if 'protected' in post['excerpt'].keys() and post['excerpt']['protected']:
                            line += "<post is protected>"
                        elif 'rendered' in post['excerpt'].keys():
                            line += "\n" + html.unescape(post['excerpt']['rendered'])
                    if 'content' in post.keys():
                        line += "\nContent: "
                        if 'protected' in post['content'].keys() and post['content']['protected']:
                            line += "<post is protected>"
                        elif 'rendered' in post['content'].keys():
                            line += "\n" + html.unescape(post['content']['rendered'])
                if 'comments' in post.keys():
                    for comment in post['comments']:
                        line += "\n\t * Comment by %s from (%s) - %s" % (comment['author_name'], comment['author_url'], comment['link'])
                print(line)
        
        if len(orphan_comments) > 0:
            # TODO: Untested code, may never be executed, I don't know how the REST API and WordPress handle post/comment link in back-end
            print()
            print("Found orphan comments! Check them right below:")
            for comment in post['comments']:
                line += "\n\t * Comment by %s from (%s) on post ID %d - %s" % (comment['author_name'], comment['author_url'], comment['post'], comment['link'])
        print()

    @staticmethod
    def display_comments(information, details=False):
        """
            Displays comments published on the WordPress instance.

            :param information: information as a JSON object
            :param details: if the details should be displayed
        """
        print()
        date_format = "%Y-%m-%dT%H:%M:%S-%Z"
        for comment in information:
            if comment is not None:
                line = ""
                if 'id' in comment.keys():
                    line += "ID: %d" % comment['id']
                if 'post' in comment.keys():
                    line += " - Post ID: %d" % comment['post'] #html.unescape(post['title']['rendered'])
                if 'author_name' in comment.keys():
                    line += " - By %s" % comment['author_name']
                if 'date' in comment.keys():
                    date_gmt = datetime.strptime(comment['date_gmt'] +
                                                "-GMT", date_format)
                    line += " on %s" % \
                            date_gmt.strftime("%d/%m/%Y at %H:%M:%S")
                if details:
                    if 'parent' in comment.keys() and comment['parent'] != 0:
                        line += "\nParent ID: " + comment['parent']
                    if 'link' in comment.keys():
                        line += "\nLink: " + comment['link']
                    if 'status' in comment.keys():
                        line += "\nStatus: " + comment['status']
                    if 'author_url' in comment.keys() and len(comment['author_url']) > 0:
                        line += "\nAuthor URL: " + comment['author_url']
                    if 'content' in comment.keys():
                        line += "\nContent: \n" + html.unescape(comment['content']['rendered'])
                print(line)
        print()

    @staticmethod
    def display_users(information, details=False):
        """
            Displays users on the WordPress instance

            :param information: information as a JSON object
            :param details: display more details about the user
        """
        print()
        for user in information:
            if user is not None:
                line = ""
                if 'id' in user.keys():
                    line += "User ID: %d\n" % user['id']
                if 'name' in user.keys():
                    line += "    Display name: %s\n" % user['name']
                if 'slug' in user.keys():
                    line += "    User name (probable): %s\n" % user['slug']
                if 'description' in user.keys():
                    line += "    User description: %s\n" % user['description']
                if 'url' in user.keys():
                    line += "    User website: %s\n" % user['url']
                if 'link' in user.keys():
                    line += "    User personal page: %s\n" % user['link']
                if details:
                    if "avatar_urls" in user.keys() and type(user["avatar_urls"]) is dict and len(user["avatar_urls"].keys()) > 0:
                        line += "    Avatars: \n"
                        for key, value in user["avatar_urls"].items():
                            line += "        * %s: %s\n" % (key, value)
                print(line)
        print()

    @staticmethod
    def display_categories(information, details=False):
        """
        Displays categories of the WordPress instance
        param information: information as a JSON object
        """
        print()
        for category in information:
            if category is not None:
                line = ""
                if 'id' in category.keys():
                    line += "Category ID: %d\n" % category['id']
                if 'name' in category.keys():
                    line += "    Name: %s\n" % category['name']
                if 'description' in category.keys():
                    line += "    Description: %s\n" % category['description']
                if 'count' in category.keys():
                    line += "    Number of posts: %d\n" % category['count']
                if 'link' in category.keys():
                    line += "    Page: %s\n" % category['link']
                if details:
                    if 'slug' in category.keys():
                        line += "    Slug: %s\n" % category['slug']
                    if 'taxonomy' in category.keys():
                        line += "    Taxonomy: %s\n" % category['slug']
                    if 'parent' in category.keys():
                        line += "    Parent category: "
                        if type(category['parent']) is str:
                            line += category['parent']
                        elif type(category['parent']) is int:
                            line += "%d" % category['parent']
                        else:
                            line += "Unknown"
                        line += "\n"
                print(line)
        print()

    @staticmethod
    def display_tags(information, details=False):
        """
        Displays tags of the WordPress instance
        param information: information as a JSON object
        """
        print()
        for tag in information:
            if tag is not None:
                line = ""
                if 'id' in tag.keys():
                    line += "Tag ID: %d\n" % tag['id']
                if 'name' in tag.keys():
                    line += "    Name: %s\n" % tag['name']
                if 'description' in tag.keys():
                    line += "    Description: %s\n" % tag['description']
                if 'count' in tag.keys():
                    line += "    Number of posts: %d\n" % tag['count']
                if 'link' in tag.keys():
                    line += "    Page: %s\n" % tag['link']
                if details:
                    if 'slug' in tag.keys():
                        line += "    Slug: %s\n" % tag['slug']
                    if 'taxonomy' in tag.keys():
                        line += "    Taxonomy: %s\n" % tag['slug']
                print(line)
        print()

    @staticmethod
    def display_media(information, details=False):
        """
            Displays media objects of the WordPress instance

            :param information: information as a JSON object
            :param details: if the details should be displayed
        """
        print()
        date_format = "%Y-%m-%dT%H:%M:%S-%Z"
        for media in information:
            if media is not None:
                line = ""
                if 'id' in media.keys():
                    line += "Media ID: %d\n" % media['id']
                if 'title' in media.keys() and 'rendered' in media['title']:
                    line += "    Media title: %s\n" % \
                            html.unescape(media['title']['rendered'])
                if 'date_gmt' in media.keys():
                    date_gmt = datetime.strptime(media['date_gmt'] +
                                                "-GMT", date_format)
                    line += "    Upload date (GMT): %s\n" % \
                            date_gmt.strftime("%d/%m/%Y %H:%M:%S")
                if 'media_type' in media.keys():
                    line += "    Media type: %s\n" % media['media_type']
                if 'mime_type' in media.keys():
                    line += "    Mime type: %s\n" % media['mime_type']
                if 'link' in media.keys():
                    line += "    Page: %s\n" % media['link']
                if 'source_url' in media.keys():
                    line += "    Source URL: %s\n" % media['source_url']
                if details:
                    if 'slug' in media.keys():
                        line += "Slug: " + media['slug'] + "\n"
                    if 'status' in media.keys():
                        line += "Status: " + media['status'] + "\n"
                    if 'type' in media.keys():
                        line += "Type: " + media['type'] + "\n"
                    if 'author' in media.keys():
                        line += "Author ID: %d\n" % media['author']
                    if 'alt_text' in media.keys():
                        line += "Alt text: " + media['alt_text'] + "\n"
                    if 'comment_status' in media.keys():
                        line += "Comment status: " + media['comment_status'] + "\n"
                    if 'post' in media.keys():
                        line += "Post or page ID: %d\n" % media['post']
                    if 'description' in media.keys() and media['description']['rendered']:
                        line += "Description: \n" + html.unescape(media['description']['rendered']) + "\n"
                    if 'caption' in media.keys() and media['caption']['rendered']:
                        line += "Caption: \n" + html.unescape(media['caption']['rendered']) + "\n"
                print(line)
        print()

    @staticmethod
    def display_pages(information, details=False):
        """
            Displays pages published on the WordPress instance

            :param information: information as a JSON object
            :param details: if the details should be displayed
        """
        print()
        for page in information:
            if page is not None:
                line = ""
                if 'id' in page.keys():
                    line += "ID: %d" % page['id']
                if 'title' in page.keys() and 'rendered' in page['title']:
                    line += " - " + html.unescape(page['title']['rendered'])
                if 'link' in page.keys():
                    line += " - " + page['link']
                if details:
                    if 'slug' in page.keys():
                        line += "\nSlug: " + page['slug']
                    if 'status' in page.keys():
                        line += "\nStatus: " + page['status']
                    if 'author' in page.keys():
                        line += "\nAuthor ID: %d" % page['author']
                    if 'comment_status' in page.keys():
                        line += "\nComment status: " + page['comment_status']
                    if 'template' in page.keys() and len(page['template']) > 0:
                        line += "\nTemplate: " + page['template']
                    if 'parent' in page.keys():
                        if page['parent'] == 0:
                            line += "\nParent: none"
                        else:
                            line += "\nParent ID: %d" % page['parent']
                    if 'excerpt' in page.keys():
                        line += "\nExcerpt: "
                        if 'protected' in page['excerpt'].keys() and page['excerpt']['protected']:
                            line += "<page is protected>"
                        elif 'rendered' in page['excerpt'].keys():
                            line += "\n" + html.unescape(page['excerpt']['rendered'])
                    if 'content' in page.keys():
                        line += "\nContent: "
                        if 'protected' in page['content'].keys() and page['content']['protected']:
                            line += "<page is protected>"
                        elif 'rendered' in page['content'].keys():
                            line += "\n" + html.unescape(page['content']['rendered'])
                print(line)
        print()

    @staticmethod
    def recurse_list_or_dict(data, tab):
        """
        Helper function to generate recursive display of API data
        """
        if type(data) is not dict and type(data) is not list:
            return tab + str(data)

        line = ""
        if type(data) is list:
            i = 0
            length = len(data)
            for value in data:
                do_jmp = True
                if type(value) is dict or type(value) is list:
                    line += InfoDisplayer.recurse_list_or_dict(value, tab+"\t")
                elif type(value) is str:
                    if "\n" in value:
                        line += "\n" + tab + "\t"
                        line += value.replace("\n", "\n"+tab+"\t")
                    else:
                        line += " "
                        line += value.replace("\n", "\n"+tab)
                        do_jmp = False
                else:
                    line += " " + str(value)
                if i < length and do_jmp:
                    line += "\n"
                i += 1
        else:
            for key,value in data.items():
                line += "\n" + tab + key
                if type(value) is dict or type(value) is list:
                    line += InfoDisplayer.recurse_list_or_dict(value, tab+"\t")
                elif type(value) is str:
                    if "\n" in value:
                        line += "\n" + tab + "\t"
                        line += value.replace("\n", "\n"+tab+"\t")
                    else:
                        line += " "
                        line += value.replace("\n", "\n"+tab)
                else:
                    line += " " + str(value)
        return line

    @staticmethod
    def display_crawled_ns(information):
        """
        Displays endpoints details published on the WordPress instance
        param information: information as a JSON object
        """
        print()
        for url,data in information.items():
            line = "\n"
            line += url
            tab = "\t"
            line += InfoDisplayer.recurse_list_or_dict(data, tab)
            print(line)
        print()
