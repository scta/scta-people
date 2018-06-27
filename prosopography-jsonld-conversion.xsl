<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  exclude-result-prefixes="xs"
  version="2.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0">
  <xsl:output method="text" media-type="application/json"></xsl:output>
  <xsl:template match="//person">
    <xsl:variable name="id" select="./@xml:id"/>
    <xsl:variable name="names" select=".//persName"/>
    <xsl:variable name="type" select="lower-case(./parent::listPerson[1]/@type)"/>
    <xsl:variable name="order" select="./note[@type='order']"/>
    <xsl:variable name="sameas" select="./note[@type='dbpedia-url'] | ./note[@type='wikidata-id']"/>
    
    <xsl:result-document method="text" href="/Users/jcwitt/Projects/scta/scta-people/graphs/{$id}.jsonld">{
  "@context": "http://scta.info/api/core/1.0/people/context.json",
  "@id": "http://scta.info/resource/<xsl:value-of select="$id"/>",
  "@type": "http://scta.info/resource/person",
  "dc:title": [<xsl:for-each select="$names">{"@value": "<xsl:value-of select="."/>", "@language": "<xsl:value-of select="@xml:lang"/>"}<xsl:if test="not(position() eq last())">,</xsl:if></xsl:for-each>],
  "sctap:personType": "http://scta.info/resource/<xsl:value-of select="$type"/>",
  "sctap:shortId": "<xsl:value-of select="$id"/>"<xsl:if test="$order">,</xsl:if>
  <xsl:if test="$order">
  "sctap:hasAffiliation":  [
    "http://scta.info/resource/<xsl:value-of select="$order"/>"</xsl:if>
      ],<xsl:if test="$sameas">
  "owl:sameAs": [<xsl:for-each select="$sameas">
      <xsl:choose>
        <xsl:when test="@type eq 'wikidata-id'">
          "<xsl:value-of select="concat('https://www.wikidata.org/wiki/Special:EntityData/', ., '.json')"/>"<xsl:if test="not(position() eq last())">,</xsl:if>
        </xsl:when>
        <xsl:otherwise>
          "<xsl:value-of select="."/>"<xsl:if test="not(position() eq last())">,</xsl:if>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
   ]
  </xsl:if>
  }
    </xsl:result-document>
  </xsl:template>
</xsl:stylesheet>